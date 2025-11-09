def create_sales_volume_refresh_log_table(cursor):
    """
    Creates the 'sales_volume_refresh_log' table to track when a sales volume
    refresh was last attempted for a card. This helps prevent redundant API calls
    for cards where data is consistently unavailable.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_volume_refresh_log (
        card_id INTEGER PRIMARY KEY,
        last_attempted_date DATETIME NOT NULL,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)
    print("Created or verified 'sales_volume_refresh_log' table.")
