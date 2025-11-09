from datetime import datetime


class PsaDAO:
    """
    Data Access Object for handling PSA population data.
    """

    def __init__(self, conn, candidates_dao=None):
        """
        Initializes the PsaDAO with a database connection.
        :param conn: An active database connection.
        """
        self.conn = conn
        self.cursor = conn.cursor()
        self.candidates_dao = candidates_dao

    def add_psa_population_from_json(self, card_id, json_data):
        """
        Parses a JSON object for PSA population data and inserts it into the
        'psa_population' table. This method expects the JSON to be "wide" and
        unpivots it into a "long" format for database storage.

        :param card_id: The ID of the card this population data belongs to.
        :param json_data: The raw JSON object containing grades and counts.
        """
        if not isinstance(json_data, dict):
            print("Error: PSA population data must be a dictionary.")
            return

        updated_date_str = json_data.get('updated_date')
        updated_date = datetime.strptime(updated_date_str, '%Y-%m-%d %H:%M:%S') if updated_date_str else None

        population_tuples = []
        for key, value in json_data.items():
            if key != 'updated_date':
                try:
                    grade = float(key)
                    population_count = int(value)
                    population_tuples.append((
                        card_id,
                        grade,
                        population_count,
                        updated_date
                    ))
                except (ValueError, TypeError):
                    print(f"Warning: Skipping invalid grade/population entry: {key}:{value}")

        if not population_tuples:
            print("No valid population data found to insert.")
            return

        # Using INSERT OR REPLACE to handle updates gracefully.
        # The UNIQUE constraint on (card_id, psa_grade) ensures that if we
        # insert a new record for an existing card/grade, it replaces the old one.
        self.cursor.executemany(
            "INSERT OR REPLACE INTO psa_population (card_id, psa_grade, population_count, updated_date) VALUES (?, ?, ?, ?)",
            population_tuples
        )
        print(f"Inserted or replaced {len(population_tuples)} rows in psa_population for card_id {card_id}.")

        # New: Update the derived analytics data after population changes.
        self.update_card_analytics(card_id)

        # Trigger financial calculation update
        if self.candidates_dao:
            self.candidates_dao.update_grading_financials(card_id)
            print(f"Triggered financial metric update for card_id {card_id}.")

        self.conn.commit()


    def get_psa_population_as_json(self, card_id):
        """
        Retrieves all PSA population data for a given card_id and reconstructs
        it into the original "wide" JSON format.

        :param card_id: The ID of the card to retrieve population data for.
        """
        self.cursor.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

        rows = self.cursor.execute(
            "SELECT psa_grade, population_count, updated_date FROM psa_population WHERE card_id = ?",
            (card_id,)
        ).fetchall()

        if not rows:
            return None

        # Reconstruct the wide JSON format
        result_json = {}
        for row in rows:
            # Format the grade back to a string key (e.g., 8.0 -> "8.0")
            grade_key = f"{row['psa_grade']:.1f}"
            result_json[grade_key] = row['population_count']

        # Add the updated_date (it's the same for all rows of a given card_id)
        first_row = rows[0]
        if first_row['updated_date']:
            result_json['updated_date'] = first_row['updated_date'].strftime('%Y-%m-%d %H:%M:%S')

        return result_json

    def update_card_analytics(self, card_id, silent=False):

        """
        Calculates and updates gem rate and population counts in the 'card_analytics' table
        for a specific card based on the data in 'psa_population'.
        This method is called automatically when PSA population is updated.
        """
        # Use a dictionary row factory for easier data access
        self.cursor.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

        query = """
            SELECT
                SUM(CASE WHEN psa_grade = 10.0 THEN population_count ELSE 0 END) as psa_10_pop,
                SUM(CASE WHEN psa_grade != 10.0 THEN population_count ELSE 0 END) as non_psa_10_pop
            FROM psa_population
            WHERE card_id = ?
        """
        self.cursor.execute(query, (card_id,))
        pop_data = self.cursor.fetchone()

        if not pop_data or pop_data['psa_10_pop'] is None:
            print(f"No population data found for card_id {card_id} to calculate analytics.")
            return

        psa_10_pop = pop_data['psa_10_pop']
        non_psa_10_pop = pop_data['non_psa_10_pop'] or 0
        total_pop = psa_10_pop + non_psa_10_pop

        gem_rate = (psa_10_pop / total_pop) if total_pop > 0 else 0

        upsert_query = """
            INSERT INTO card_analytics (card_id, psa_10_pop, non_psa_10_pop, gem_rate, last_calculated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(card_id) DO UPDATE SET
                psa_10_pop = excluded.psa_10_pop,
                non_psa_10_pop = excluded.non_psa_10_pop,
                gem_rate = excluded.gem_rate,
                last_calculated = excluded.last_calculated;
        """
        self.cursor.execute(upsert_query, (card_id, psa_10_pop, non_psa_10_pop, gem_rate))
        if not silent:
            print(f"Updated analytics for card_id {card_id}.")

        # Reset row factory to default if needed elsewhere
        self.cursor.row_factory = None

        self.conn.commit()
