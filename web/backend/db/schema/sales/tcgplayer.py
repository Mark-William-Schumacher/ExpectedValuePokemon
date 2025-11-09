def create_tcgplayer_table(cursor):
    """
    Creates the 'tcgplayer' table in the database.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tcgplayer (
        tcgplayer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_tcgplayer_id INTEGER UNIQUE,
        card_id INTEGER,
        created_at DATETIME,
        date_sold DATETIME,
        interpolated BOOLEAN,
        set_id INTEGER,
        sold_price DECIMAL(10, 2),
        FOREIGN KEY (card_id) REFERENCES card_sales(card_id)
    );
    """)
    print("Created or verified 'tcgplayer' table.")
