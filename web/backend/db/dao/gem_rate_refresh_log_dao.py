from textwrap import dedent

class GemRateRefreshLogDAO:
    """
    Data Access Object for managing the gem rate refresh log.
    """

    def __init__(self, conn):
        """
        Initializes the DAO with a database connection.
        """
        self.conn = conn
        self.cursor = conn.cursor()

    def log_batch_refresh_attempt(self, card_ids):
        """
        Logs that a refresh attempt was made for a batch of card IDs
        by inserting or updating their entries with the current timestamp.
        """
        if not card_ids:
            return

        query = dedent("""
            INSERT INTO gem_rate_refresh_log (card_id, last_attempted_date)
            VALUES (?, CURRENT_TIMESTAMP)
            ON CONFLICT(card_id) DO UPDATE SET
                last_attempted_date = excluded.last_attempted_date;
        """)

        data = [(card_id,) for card_id in card_ids]
        self.cursor.executemany(query, data)
        self.conn.commit()
        print(f"Logged gem rate refresh attempt for {len(card_ids)} cards.")