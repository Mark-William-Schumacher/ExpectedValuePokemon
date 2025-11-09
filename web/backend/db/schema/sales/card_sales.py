def create_card_sales_table(cursor):
    """
    Creates the 'card_sales' table in the database.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_sales (
        card_id INTEGER PRIMARY KEY,
        updated_date DATETIME
    );
    """)
    print("Created or verified 'card_sales' table.")