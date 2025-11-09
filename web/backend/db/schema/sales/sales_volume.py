def create_sales_volume_table(cursor):
    """
    Creates the 'sales_volume' table to store pre-calculated sales volume metrics
    for each card, based on a 30-day window from the last known sale.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_volume (
        card_id INTEGER PRIMARY KEY,
        psa10_volume INTEGER,
        non_psa10_volume INTEGER,
        last_sales_date DATETIME,
        last_calculated DATETIME,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)
    print("Created or verified 'sales_volume' table.")
