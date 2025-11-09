import sqlite3
from collections import defaultdict
from pprint import pprint
from textwrap import dedent

from core_module.card_data_utils.get_raw_to_psa10_grading_value_from_jsons import \
    get_raw_to_psa10_grading_value_from_jsons_cache

from core_module.card_data_utils.calculate_expected_value import calculate_net_gain
from core_module.utils.file_utils import save_object_to_file


class CandidatesDAO:
    """
    Data Access Object for handling queries related to finding candidate cards.
    """

    def __init__(self, conn):
        """
        Initializes the CandidatesDAO with a database connection.
        :param conn: An active database connection.
        """
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()

    def find_raw_to_psa10_grading_value(self, min_value_increase, min_psa10_price):
        """
        Finds cards where the PSA 10 price is greater than the raw price by a certain amount,
        and the PSA 10 price is above a minimum threshold.

        :param min_value_increase: The minimum required increase in value from a raw card to a PSA 10.
        :param min_psa10_price: The minimum required price for the PSA 10 card.
        :return: A list of card IDs for the candidates.
        """
        query = """
                SELECT cs.card_id
                FROM card_stats cs
                WHERE cs.source IN (0.0, 10.0)
                GROUP BY cs.card_id
                HAVING COUNT(DISTINCT cs.source) = 2 -- Ensure both raw and PSA 10 prices exist
                   AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                        MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
                   AND MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?; \
                """
        self.cursor.execute(query, (min_value_increase, min_psa10_price))
        rows = self.cursor.fetchall()
        return [row['card_id'] for row in rows]

    def find_profitable_candidates(self, min_value_increase, min_psa10_price, grading_cost, min_net_gain):
        """
        Finds profitable card candidates by performing price and net gain calculations in a single, efficient query.
        This is the primary method to use for finding profitable cards.

        :param min_value_increase: The minimum required increase in value from a raw card to a PSA 10.
        :param min_psa10_price: The minimum required price for the PSA 10 card.
        :param grading_cost: The cost of grading a single card.
        :param min_net_gain: The minimum net gain required for a card to be included.
        :return: A list of card data dictionaries for the profitable candidates.
        """
        query = """
        WITH potential_candidates AS (
                SELECT
                    cs.card_id,
                    MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) as raw_price,
                    MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) as psa_10_price
                FROM
                    card_stats cs
                WHERE
                    cs.source IN (0.0, 10.0)
                GROUP BY
                    cs.card_id
                HAVING
                    COUNT(DISTINCT cs.source) = 2
                    AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                         MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
                    AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?)
            )
            SELECT
                c.card_id,
                c.name,
                pc.raw_price,
                pc.psa_10_price,
                ca.gem_rate,
                ca.psa_10_pop
            FROM
                cards c
            JOIN
                potential_candidates pc ON c.card_id = pc.card_id
            INNER JOIN
                card_analytics ca ON c.card_id = ca.card_id;
        """

        self.cursor.execute(query, (min_value_increase, min_psa10_price))
        card_data_rows = self.cursor.fetchall()

        profitable_candidates = []
        for row in card_data_rows:
            card_data = dict(row)
            if card_data.get('gem_rate') is None:
                print(f"Skipping card {card_data.get('card_id')} due to missing data for calculation.")
                continue

            try:
                ev, total_cost, net_gain, lucrative_factor = calculate_net_gain(card_data, grading_cost)
                if net_gain >= min_net_gain:
                    card_data['net_gain'] = net_gain
                    card_data['lucrative_factor'] = lucrative_factor
                    card_data['total_cost'] = total_cost
                    card_data['expected_value'] = ev
                    profitable_candidates.append(card_data)
            except (TypeError, KeyError) as e:
                print(f"Skipping card {card_data.get('card_id')} due to missing data for calculation: {e}")

        return profitable_candidates

    def find_profitable_candidates2(self, min_value_increase, min_psa10_price, grading_cost, min_net_gain):
        """
        Finds profitable card candidates and returns them in a rich, structured format
        by joining data from multiple tables.

        :param min_value_increase: The minimum required increase in value from a raw card to a PSA 10.
        :param min_psa10_price: The minimum required price for the PSA 10 card.
        :param grading_cost: The cost of grading a single card.
        :param min_net_gain: The minimum net gain required for a card to be included.
        :return: A list of structured card data dictionaries for the profitable candidates.
        """
        # 1. Get the initial list of card IDs that meet the price criteria
        initial_candidates_query = dedent("""
            SELECT cs.card_id FROM card_stats cs
            WHERE cs.source IN (0.0, 10.0)
            GROUP BY cs.card_id
            HAVING COUNT(DISTINCT cs.source) = 2
               AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                    MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
               AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?);
        """)
        self.cursor.execute(initial_candidates_query, (min_value_increase, min_psa10_price))
        candidate_ids = [row['card_id'] for row in self.cursor.fetchall()]

        if not candidate_ids:
            return []

        placeholders = ','.join('?' for _ in candidate_ids)

        # 2. Get the main data for these candidates, filtering by net_gain
        main_data_query = dedent(f"""
            SELECT
                c.card_id, c.set_id, c.name, c.num, c.img_url, c.language, c.release_date, c.secret, c.hot, c.live, c.stat_url,
                s.name as set_name, s.code as set_code,
                ca.psa_10_pop, ca.non_psa_10_pop, ca.gem_rate,
                gf.net_gain, gf.lucrative_factor, gf.total_cost, gf.expected_value,
                sv.psa10_volume, sv.non_psa10_volume, sv.last_sales_date
            FROM cards c
            JOIN sets s ON c.set_id = s.set_id
            JOIN card_analytics ca ON c.card_id = ca.card_id
            JOIN grading_financials gf ON c.card_id = gf.card_id
            LEFT JOIN sales_volume sv ON c.card_id = sv.card_id
            WHERE c.card_id IN ({placeholders}) AND gf.net_gain >= ?
        """)
        final_params = candidate_ids + [min_net_gain]
        self.cursor.execute(main_data_query, final_params)
        main_data_rows = self.cursor.fetchall()

        if not main_data_rows:
            return []

        final_card_ids = [row['card_id'] for row in main_data_rows]
        final_placeholders = ','.join('?' for _ in final_card_ids)

        # 3. Batch fetch all related stats
        stats_query = dedent(f"SELECT card_id, avg, source FROM card_stats WHERE card_id IN ({final_placeholders})")
        self.cursor.execute(stats_query, final_card_ids)
        stats_map = defaultdict(list)
        for row in self.cursor.fetchall():
            stats_map[row['card_id']].append(dict(row))

            # 4. Batch fetch recent raw eBay sales (last 90 days)
        sales_query = dedent(f"""
            WITH ranked_sales AS (
                SELECT
                    card_id, date_sold, ebay_handle, ebay_item_id, source_transaction_id as id, marketplace, num_bids, psa_grade, set_id, sold_price, title,
                    ROW_NUMBER() OVER(PARTITION BY card_id ORDER BY date(date_sold) DESC) as rn
                FROM
                    transactions
                WHERE
                    card_id IN ({final_placeholders}) AND psa_grade = 0.0
            )
            SELECT card_id, date_sold, ebay_handle, ebay_item_id, id, marketplace, num_bids, psa_grade, set_id, sold_price, title
            FROM ranked_sales
            WHERE rn <= 10
         """)
        self.cursor.execute(sales_query, final_card_ids)
        sales_map = defaultdict(list)
        for row in self.cursor.fetchall():
            sales_map[row['card_id']].append(dict(row))

        # 5. Assemble the final structured data
        result = []
        for row in main_data_rows:
            card_id = row['card_id']
            card_stats = stats_map.get(card_id, [])

            raw_price = next((stat['avg'] for stat in card_stats if stat['source'] == 0.0), None)
            psa_10_price = next((stat['avg'] for stat in card_stats if stat['source'] == 10.0), None)

            # Re-format release date to YYYY-MM-DD
            release_date_iso = row['release_date']
            formatted_release_date = release_date_iso.split('T')[0] if release_date_iso else None

            structured_card = {
                "name": row['name'],
                "raw_price": raw_price,
                "psa_10_price": psa_10_price,
                "id": card_id,
                "set_code": row['set_code'],
                "stats_url": row['stat_url'],
                "release_date": formatted_release_date,
                "set_name": row['set_name'],
                "set_id": row['set_id'],
                "card_data": {
                    "hot": row['hot'],
                    "id": card_id,
                    "img_url": row['img_url'],
                    "language": row['language'],
                    "live": bool(row['live']),
                    "name": row['name'],
                    "num": row['num'],
                    "release_date": formatted_release_date,
                    "secret": bool(row['secret']),
                    "set_code": row['set_code'],
                    "set_id": row['set_id'],
                    "set_name": row['set_name'],
                    "stat_url": row['stat_url'],
                    "stats": card_stats
                },
                "psa_10_pop": row['psa_10_pop'],
                "non_psa_10_pop": row['non_psa_10_pop'],
                "gem_rate": row['gem_rate'],
                "ev": row['expected_value'],
                "total_cost": row['total_cost'],
                "net_gain": row['net_gain'],
                "lucrative_factor": row['lucrative_factor'],
                "psa10_volume": row['psa10_volume'] or 0,
                "non_psa10_volume": row['non_psa10_volume'] or 0,
                "last_sales_date": row['last_sales_date'] or 0,
                "recent_raw_ebay_sales": sales_map.get(card_id, [])
            }
            result.append(structured_card)

        return result


    def filter_candidates_by_net_gain(self, candidate_ids, grading_cost, min_net_gain):
        """
        Filters a list of candidate card IDs based on a calculated net gain.
        This demonstrates a hybrid approach: using SQL to fetch data efficiently
        and Python to handle complex business logic.

        :param candidate_ids: A list of card IDs to filter.
        :param grading_cost: The cost of grading a single card.
        :param min_net_gain: The minimum net gain required for a card to be included.
        :return: A list of card IDs that meet the net gain criteria.
        """
        if not candidate_ids:
            return []

        placeholders = ','.join('?' for _ in candidate_ids)

        # Step 1: Use a single SQL query to gather all necessary data.
        query = f"""
            SELECT
                c.card_id,
                raw_stats.avg as raw_price,
                psa10_stats.avg as psa_10_price,
                ca.gem_rate,
                ca.psa_10_pop
                /* Add other fields from 'cards' or 'card_analytics' if calculate_net_gain needs them */
            FROM
                cards c
            JOIN card_stats raw_stats ON c.card_id = raw_stats.card_id AND raw_stats.source = 0.0
            JOIN card_stats psa10_stats ON c.card_id = psa10_stats.card_id AND psa10_stats.source = 10.0
            LEFT JOIN card_analytics ca ON c.card_id = ca.card_id
            WHERE
                c.card_id IN ({placeholders})
        """

        self.cursor.execute(query, candidate_ids)
        card_data_rows = self.cursor.fetchall()

        # Step 2: Use Python for the complex calculation logic.
        profitable_card_ids = []
        for row in card_data_rows:
            card_data = dict(row)
            if card_data.get('gem_rate') is None:
                continue

            try:
                # Reuse the existing, tested business logic
                _ev, _total_cost, net_gain, _lucrative_factor = calculate_net_gain(card_data, grading_cost)
                if net_gain >= min_net_gain:
                    profitable_card_ids.append(card_data['card_id'])
            except (TypeError, KeyError) as e:
                # This helps debug if `calculate_net_gain` expects other data
                print(f"Skipping card {card_data['card_id']} due to missing data for calculation: {e}")

        return profitable_card_ids

    def get_cards_with_analytics(self):
        """
        Retrieves the name and gem rate for all cards that have an entry
        in the card_analytics table.

        :return: A list of dictionaries, each containing 'name' and 'gem_rate'.
        """
        query = dedent("""
               SELECT
                   c.name,
                   ca.gem_rate
               FROM
                   cards c
               INNER JOIN
                   card_analytics ca ON c.card_id = ca.card_id;
           """)
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def update_grading_financials(self, card_id, grading_cost=29):
        """
        Calculates and updates the financial metrics for a specific card
        in the 'grading_financials' table.
        This method should be called whenever underlying data (prices, gem rate) changes.

        :param card_id: The ID of the card to update.
        :param grading_cost: The assumed cost of grading.
        """
        # Step 1: Gather all necessary data in one query
        query = """
            SELECT
                cs_raw.avg as raw_price,
                cs_psa10.avg as psa_10_price,
                ca.gem_rate
            FROM cards c
            LEFT JOIN card_stats cs_raw ON c.card_id = cs_raw.card_id AND cs_raw.source = 0.0
            LEFT JOIN card_stats cs_psa10 ON c.card_id = cs_psa10.card_id AND cs_psa10.source = 10.0
            LEFT JOIN card_analytics ca ON c.card_id = ca.card_id
            WHERE c.card_id = ?
            """
        self.cursor.execute(query, (card_id,))
        data = self.cursor.fetchone()

        if not all(data.keys()):
            # print(f"Skipping financials for card {card_id}, missing required data (price or gem rate).")
            return

        # Step 2: Perform calculations using your existing logic
        try:
            card_data = dict(data)
            ev, total_cost, net_gain, lucrative_factor = calculate_net_gain(card_data, grading_cost)

            # Step 3: Upsert the results into the new table
            upsert_query = dedent("""
                    INSERT INTO grading_financials (card_id, net_gain, lucrative_factor, total_cost, expected_value, last_calculated)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(card_id) DO UPDATE SET
                        net_gain = excluded.net_gain,
                        lucrative_factor = excluded.lucrative_factor,
                        total_cost = excluded.total_cost,
                        expected_value = excluded.expected_value,
                        last_calculated = excluded.last_calculated;
                """)
            self.cursor.execute(upsert_query, (card_id, net_gain, lucrative_factor, total_cost, ev))
            self.conn.commit()
        except (TypeError, KeyError) as e:
            pass
            # print(f"Could not calculate financials for card {card_id}: {e}")

    def find_profitable_candidates_without_gem_rate(self, min_value_increase, min_psa10_price,
                                                    days_since_last_attempt=7):
        """
        Finds candidate cards that meet price criteria, do NOT have a gem rate,
        and have not had a refresh attempt within the specified number of days.

        :param min_value_increase: The minimum required increase in value from a raw card to a PSA 10.
        :param min_psa10_price: The minimum required price for the PSA 10 card.
        :param days_since_last_attempt: The number of days to wait before re-attempting a refresh.
        :return: A list of card data dictionaries for candidates missing analytics.
        """
        query = dedent(f"""
               WITH potential_candidates AS (
                   SELECT
                       cs.card_id,
                       MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) as raw_price,
                       MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) as psa_10_price
                   FROM
                       card_stats cs
                   WHERE
                       cs.source IN (0.0, 10.0)
                   GROUP BY
                       cs.card_id
                   HAVING
                       COUNT(DISTINCT cs.source) = 2
                       AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                            MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
                       AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?)
               )
               SELECT
                   c.card_id,
                   c.name,
                   pc.raw_price,
                   pc.psa_10_price
               FROM
                   cards c
               JOIN
                   potential_candidates pc ON c.card_id = pc.card_id
               LEFT JOIN
                   card_analytics ca ON c.card_id = ca.card_id
               LEFT JOIN
                   gem_rate_refresh_log grrl ON c.card_id = grrl.card_id
               WHERE
                   ca.card_id IS NULL
                   AND (grrl.last_attempted_date IS NULL OR grrl.last_attempted_date <= date('now', '-{days_since_last_attempt} days'));
           """)
        self.cursor.execute(query, (min_value_increase, min_psa10_price))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_card_id_list_of_profitable_cards_without_gem_rate(self, min_value_increase =70, min_psa10_price=120):
        # --- Main Logic ---
        # 1. Get the list of candidate dictionaries from the DAO.
        candidates_without_gem_rate = self.find_profitable_candidates_without_gem_rate(min_value_increase,
                                                                                       min_psa10_price,
                                                                                       days_since_last_attempt=7)

        # 2. Use a list comprehension to extract only the 'card_id' from each dictionary.
        card_ids = [candidate['card_id'] for candidate in candidates_without_gem_rate]

        # 3. Sort the list of IDs in descending (highest to lowest) order.
        sorted_card_ids = sorted(card_ids, reverse=True)

        # --- Output the final result ---
        print("List of profitable card IDs without a gem rate (sorted high to low):")
        print(len(sorted_card_ids))
        return sorted_card_ids

    def find_profitable_candidates_without_sales_volume(self, min_value_increase, min_psa10_price,
                                                        days_since_last_attempt=7):
        """
        Finds candidate cards that meet price criteria, do NOT have sales volume data,
        and have not had a refresh attempt within the specified number of days.

        :param min_value_increase: Minimum value increase from raw to PSA 10.
        :param min_psa10_price: Minimum price for the PSA 10 card.
        :param days_since_last_attempt: The number of days to wait before re-attempting a refresh.
        :return: A list of card data dictionaries for candidates needing a sales volume refresh.
        """
        query = dedent(f"""
              WITH potential_candidates AS (
                  SELECT
                      cs.card_id,
                      MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) as raw_price,
                      MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) as psa_10_price
                  FROM
                      card_stats cs
                  WHERE
                      cs.source IN (0.0, 10.0)
                  GROUP BY
                      cs.card_id
                  HAVING
                      COUNT(DISTINCT cs.source) = 2
                      AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                           MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
                      AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?)
              )
              SELECT
                  c.card_id,
                  c.name,
                  pc.raw_price,
                  pc.psa_10_price
              FROM
                  cards c
              JOIN
                  potential_candidates pc ON c.card_id = pc.card_id
              LEFT JOIN
                  sales_volume sv ON c.card_id = sv.card_id
              LEFT JOIN
                  sales_volume_refresh_log svrl ON c.card_id = svrl.card_id
              WHERE
                  sv.card_id IS NULL
                  AND (svrl.last_attempted_date IS NULL OR svrl.last_attempted_date <= date('now', '-{days_since_last_attempt} days'));
          """)
        self.cursor.execute(query, (min_value_increase, min_psa10_price))
        return [dict(row) for row in self.cursor.fetchall()]


    def find_profitable_candidates_without_sales_volume_without_date(self, min_value_increase, min_psa10_price,
                                                        days_since_last_attempt=7):
        """
        Finds candidate cards that meet price criteria, do NOT have sales volume data,
        and have not had a refresh attempt within the specified number of days.

        :param min_value_increase: Minimum value increase from raw to PSA 10.
        :param min_psa10_price: Minimum price for the PSA 10 card.
        :param days_since_last_attempt: The number of days to wait before re-attempting a refresh.
        :return: A list of card data dictionaries for candidates needing a sales volume refresh.
        """
        query = dedent(f"""
              WITH potential_candidates AS (
                  SELECT
                      cs.card_id,
                      MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) as raw_price,
                      MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) as psa_10_price
                  FROM
                      card_stats cs
                  WHERE
                      cs.source IN (0.0, 10.0)
                  GROUP BY
                      cs.card_id
                  HAVING
                      COUNT(DISTINCT cs.source) = 2
                      AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) >
                           MAX(CASE WHEN cs.source = 0.0 THEN cs.avg END) + ?)
                      AND (MAX(CASE WHEN cs.source = 10.0 THEN cs.avg END) > ?)
              )
              SELECT
                  c.card_id,
                  c.name,
                  pc.raw_price,
                  pc.psa_10_price
              FROM
                  cards c
              JOIN
                  potential_candidates pc ON c.card_id = pc.card_id
              LEFT JOIN
                  sales_volume sv ON c.card_id = sv.card_id
              LEFT JOIN
                  sales_volume_refresh_log svrl ON c.card_id = svrl.card_id
              WHERE
                  sv.card_id IS NULL;
          """)
        self.cursor.execute(query, (min_value_increase, min_psa10_price))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_cards_by_set_names(self, set_names):
        """
        Retrieves all cards from a list of set names.
        :param set_names: A list of set names to search for.
        :return: A list of card data dictionaries.
        """
        if not set_names:
            return []

        placeholders = ','.join('?' for _ in set_names)
        query = f"""
            SELECT
                c.card_id, c.name, c.release_date, s.name as set_name
            FROM
                cards c
            JOIN
                sets s ON c.set_id = s.set_id
            WHERE
                s.name IN ({placeholders});
        """
        self.cursor.execute(query, set_names)
        return [dict(row) for row in self.cursor.fetchall()]



if __name__ == "__main__":
    from web.backend.containers import AppContainer

    # 1. Create an instance of the application's DI container.
    container = AppContainer()
    # This wires up the container's lifecycle to the application's scope.
    # For a script, we do this manually.
    container.wire(modules=[__name__])

    candidates_dao = container.candidates_dao()
    candidates = candidates_dao.find_raw_to_psa10_grading_value(70, 120)
    print(candidates)
    print(len(candidates))

    can = get_raw_to_psa10_grading_value_from_jsons_cache()
    print(len(can))

    # candidates2 = candidates_dao.find_profitable_candidates2(
    #     min_value_increase=70,
    #     min_psa10_price=120,
    #     grading_cost=40,
    #     min_net_gain=60
    # )
    #
    #
    # # --- Main Logic ---
    # # 1. Get the list of candidate dictionaries from the DAO.
    # candidates_without_gem_rate = candidates_dao.find_profitable_candidates_without_gem_rate(70, 120)
    #
    # # 2. Use a list comprehension to extract only the 'card_id' from each dictionary.
    # card_ids = [candidate['card_id'] for candidate in candidates_without_gem_rate]
    #
    # # 3. Sort the list of IDs in descending (highest to lowest) order.
    # sorted_card_ids = sorted(card_ids, reverse=True)
    #
    # # --- Output the final result ---
    # print("List of profitable card IDs without a gem rate (sorted high to low):")
    # print(len(sorted_card_ids))
    # print(sorted_card_ids)
    #
    #
    # print("List of profitable candidate without sales volume:")
    # without_sales_volume = candidates_dao.find_profitable_candidates_without_sales_volume(20,70)
    # print(len(without_sales_volume))
    # card_ids_without_volume = [candidate['card_id'] for candidate in without_sales_volume]
    # print(card_ids_without_volume)
    #
    #
    # # Save the results of candidates2 to a file instead of printing
    # save_object_to_file(candidates2, "candidates2.json", directory="cache", overwrite=True)
    # print(f"\nSaved {len(candidates2)} profitable candidates to cache/candidates2.json")

