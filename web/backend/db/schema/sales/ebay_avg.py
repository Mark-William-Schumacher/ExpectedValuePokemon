def create_ebay_avg_table(cursor):
    """
    Creates the 'ebay_avg' table in the database.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ebay_avg (
        ebay_avg_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER,
        date_sold DATETIME,
        psa_grade DECIMAL(3, 1),
        sold_price DECIMAL(10, 2),
        volume INTEGER,
        FOREIGN KEY (card_id) REFERENCES card_sales(card_id)
    );
    """)
    print("Created or verified 'ebay_avg' table.")
