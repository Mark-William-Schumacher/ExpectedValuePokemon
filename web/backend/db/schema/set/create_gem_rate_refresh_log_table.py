def create_gem_rate_refresh_log_table(cursor):
    """
    Creates the 'gem_rate_refresh_log' table to track when a gem rate
    refresh was last attempted for a card. This helps prevent redundant API calls.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gem_rate_refresh_log (
        card_id INTEGER PRIMARY KEY,
        last_attempted_date DATETIME NOT NULL,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)
    print("Created or verified 'gem_rate_refresh_log' table.")
