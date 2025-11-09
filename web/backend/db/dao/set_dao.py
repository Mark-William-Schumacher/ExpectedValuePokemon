import sqlite3
from datetime import datetime


class SetDAO:
    """
    Data Access Object for handling card set related database operations.
    """

    def __init__(self, conn, candidates_dao=None):
        """
        Initializes the SetDAO with a database connection.
        :param conn: An active database connection.
        """
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.cursor = conn.cursor()
        self.candidates_dao = candidates_dao

    def add_set_from_json(self, json_data):
        """
        Parses a JSON object for a card set and upserts (inserts or updates) the data
        into the 'sets', 'cards', and 'card_stats' tables.
        """
        cards_data = json_data.get('data', [])
        if not cards_data:
            print("Error: No card data found in the JSON response.")
            return

        # --- 1. Upsert the Set ---
        # This part already correctly handles upserting the set's top-level info.
        first_card = cards_data[0]
        set_info = {
            'id': first_card.get('set_id'),
            'name': first_card.get('set_name'),
            'code': first_card.get('set_code'),
            'updated_date': datetime.strptime(json_data.get('updated_date'), '%Y-%m-%d %H:%M:%S') if json_data.get(
                'updated_date') else None
        }
        self._upsert_set(set_info)

        # --- 2. Prepare 'cards' and 'card_stats' data for bulk upsert ---
        card_tuples = []
        card_stats_tuples = []

        for card in cards_data:
            card_tuples.append((
                card.get('id'),
                card.get('set_id'),
                card.get('name'),
                card.get('num'),
                card.get('img_url'),
                card.get('language'),
                datetime.strptime(card.get('release_date'), '%Y-%m-%d').isoformat(),
                card.get('secret'),
                card.get('hot'),
                card.get('live'),
                card.get('stat_url')
            ))

            for stat in card.get('stats', []):
                card_stats_tuples.append((
                    card.get('id'),
                    stat.get('avg'),
                    stat.get('source')
                ))

        # --- 3. Bulk upsert data using ON CONFLICT DO UPDATE ---

        # Upsert into the 'cards' table
        cards_query = """
            INSERT INTO cards (card_id, set_id, name, num, img_url, language, release_date, secret, hot, live, stat_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(card_id) DO UPDATE SET
                set_id=excluded.set_id,
                name=excluded.name,
                num=excluded.num,
                img_url=excluded.img_url,
                language=excluded.language,
                release_date=excluded.release_date,
                secret=excluded.secret,
                hot=excluded.hot,
                live=excluded.live,
                stat_url=excluded.stat_url;
        """
        self.cursor.executemany(cards_query, card_tuples)
        print(f"Upserted {len(card_tuples)} rows into cards.")

        # Upsert into the 'card_stats' table
        # This assumes a UNIQUE constraint on (card_id, source) in the card_stats table.
        card_stats_query = """
            INSERT INTO card_stats (card_id, avg, source)
            VALUES (?, ?, ?)
            ON CONFLICT(card_id, source) DO UPDATE SET
                avg=excluded.avg;
        """
        self.cursor.executemany(card_stats_query, card_stats_tuples)
        print(f"Upserted {len(card_stats_tuples)} rows into card_stats.")

        # Commit all transactions at once
        self.conn.commit()
        print("Successfully upserted set data to the database.")

        # Trigger an update for the financial metrics of each affected card.
        if self.candidates_dao:
            card_ids = [c[0] for c in card_tuples]
            for card_id in card_ids:
                self.candidates_dao.update_grading_financials(card_id)
            print(f"Triggered financial metric updates for {len(card_ids)} cards.")

    def _upsert_set(self, set_info):
        """Helper to handle the insert/update logic for the sets table."""
        self.cursor.execute(
            "INSERT OR IGNORE INTO sets (set_id, name, code) VALUES (?, ?, ?)",
            (set_info['id'], set_info['name'], set_info['code'])
        )

        if set_info.get('updated_date'):
            self.cursor.execute(
                "UPDATE sets SET updated_date = ? WHERE set_id = ?",
                (set_info['updated_date'], set_info['id'])
            )
        print(f"Upserted set_id {set_info['id']} into sets.")

    def get_set_as_json(self, set_id):
        """
        Retrieves all data for a given set_id from the database
        and reconstructs it into the original JSON format.
        """
        set_row = self.cursor.execute("SELECT * FROM sets WHERE set_id = ?", (set_id,)).fetchone()
        if not set_row:
            return None

        result = {
            "updated_date": set_row["updated_date"].strftime('%Y-%m-%d %H:%M:%S') if set_row["updated_date"] else None
        }

        card_rows = self.cursor.execute("SELECT * FROM cards WHERE set_id = ?", (set_id,)).fetchall()
        if not card_rows:

            result['data'] = []
            return result

        card_ids = [row["card_id"] for row in card_rows]
        placeholders = ','.join('?' for _ in card_ids)
        all_stats_rows = self.cursor.execute(
            f"SELECT card_id, avg, source FROM card_stats WHERE card_id IN ({placeholders})",
            card_ids
        ).fetchall()

        stats_map = {}
        for stat_row in all_stats_rows:
            card_id = stat_row["card_id"]
            if card_id not in stats_map:
                stats_map[card_id] = []
            stats_map[card_id].append({"avg": stat_row["avg"], "source": stat_row["source"]})

        data_list = []
        for card_row in card_rows:
            card_id = card_row["card_id"]
            card_dict = {
                "hot": card_row["hot"],
                "id": card_id,
                "img_url": card_row["img_url"],
                "language": card_row["language"],
                "live": bool(card_row["live"]),
                "name": card_row["name"],
                "num": card_row["num"],
                "release_date": card_row["release_date"].strftime('%Y-%m-%d') if card_row["release_date"] else None,
                "secret": bool(card_row["secret"]),
                "set_code": set_row["code"],
                "set_id": card_row["set_id"],
                "set_name": set_row["name"],
                "stat_url": card_row["stat_url"],
                "stats": stats_map.get(card_id, [])
            }
            data_list.append(card_dict)

        result['data'] = data_list
        return result

    def add_set_details_from_json(self, json_data):
        """
        Parses a JSON object for set details and inserts the data into the
        'set_details' table. It also ensures a corresponding entry exists
        in the 'sets' table without modifying any existing 'updated_date'.
        """
        set_details_data = json_data.get('data', [])
        if not set_details_data:
            print("Error: No set details data found in the JSON response.")
            return

        # Extract top-level updated date for set details
        updated_date_str = json_data.get('updated_date')
        details_updated_date = None
        if updated_date_str:
            details_updated_date = datetime.strptime(updated_date_str, '%Y-%m-%d %H:%M:%S')

        set_details_tuples = []
        set_tuples = []

        for set_detail in set_details_data:
            # Prepare data for 'set_details' table
            release_date_str = set_detail.get('release_date')
            release_date = None
            if release_date_str:
                # The format is 'Fri, 18 Jul 2025 00:00:00 GMT'
                release_date = datetime.strptime(release_date_str, '%a, %d %b %Y %H:%M:%S %Z')

            set_details_tuples.append((
                set_detail.get('id'),
                set_detail.get('language'),
                release_date,
                details_updated_date
            ))

            # Prepare basic set info for the 'sets' table to ensure it exists.
            # The 'updated_date' will remain NULL for new entries, and this
            # statement will not affect existing entries.
            set_tuples.append((
                set_detail.get('id'),
                set_detail.get('name'),
                set_detail.get('code')
            ))

        # --- 1. Bulk insert parent data first ('sets') ---
        # Using INSERT OR IGNORE to create new sets without touching existing ones.
        self.cursor.executemany(
            "INSERT OR IGNORE INTO sets (set_id, name, code) VALUES (?, ?, ?)",
            set_tuples
        )
        print(f"Inserted or ignored {len(set_tuples)} rows into sets.")

        # --- 2. Bulk insert 'set_details' data ---
        # Using INSERT OR REPLACE to update details, including the new updated_date.
        self.cursor.executemany(
            "INSERT OR REPLACE INTO set_details (set_id, language, release_date, updated_date) VALUES (?, ?, ?, ?)",
            set_details_tuples
        )
        print(f"Inserted or replaced {len(set_details_tuples)} rows into set_details.")

        self.conn.commit()
        print("Successfully added set details data to the database.")

    def get_set_details_as_json(self, set_id):
        """
        Retrieves details for a given set_id from the database
        and reconstructs it into a JSON-friendly dictionary, including both
        set details and card info update timestamps.
        """
        query = """
            SELECT
                s.set_id,
                s.name,
                s.code,
                s.updated_date as card_info_updated_date,
                sd.language,
                sd.release_date,
                sd.updated_date as set_details_updated_date
            FROM sets s
            LEFT JOIN set_details sd ON s.set_id = sd.set_id
            WHERE s.set_id = ?
        """
        set_row = self.cursor.execute(query, (set_id,)).fetchone()

        if not set_row:
            return None

        release_date = set_row["release_date"]
        formatted_release_date = None
        if release_date:
            # Format back to the original string format for consistency
            formatted_release_date = release_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

        card_info_updated_date = set_row["card_info_updated_date"]
        formatted_card_info_updated_date = None
        if card_info_updated_date:
            formatted_card_info_updated_date = card_info_updated_date.strftime('%Y-%m-%d %H:%M:%S')

        set_details_updated_date = set_row["set_details_updated_date"]
        formatted_set_details_updated_date = None
        if set_details_updated_date:
            formatted_set_details_updated_date = set_details_updated_date.strftime('%Y-%m-%d %H:%M:%S')

        set_details_dict = {
            "id": set_row["set_id"],
            "name": set_row["name"],
            "code": set_row["code"],
            "language": set_row["language"],
            "release_date": formatted_release_date,
            "card_info_updated_date": formatted_card_info_updated_date,
            "set_details_updated_date": formatted_set_details_updated_date
        }

        return set_details_dict

    def get_stale_outdated_sets_list(self, days: int):
        GET_UNIQUE_SETS_SORTED_BY_LAST_UPDATE = """
               SELECT
                  s.set_id,
                  s.name,
                  s.code,
                  s.updated_date
              FROM sets s
              WHERE s.updated_date IS NOT NULL AND s.updated_date < date('now', '-' || ? || ' days')
              ORDER BY s.updated_date DESC
          """
        try:
            self.cursor.execute(GET_UNIQUE_SETS_SORTED_BY_LAST_UPDATE, (days,))
            stale_sets =  self.cursor.fetchall()
            if stale_sets:
                return [row['set_id'] for row in stale_sets]
        except Exception as e:
            print(f"Error while getting unique sets sorted by last update: {e}")
            return None

