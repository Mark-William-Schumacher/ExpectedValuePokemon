def create_cards_table(cursor):
    """
    Creates the 'cards' table to store individual card details.
    Each card is linked to a set via the 'set_id' foreign key.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        card_id INTEGER PRIMARY KEY,
        set_id INTEGER,
        name TEXT NOT NULL,
        num TEXT,
        img_url TEXT,
        language TEXT,
        release_date DATETIME,
        secret BOOLEAN,
        hot INTEGER,
        live BOOLEAN,
        stat_url TEXT,
        FOREIGN KEY (set_id) REFERENCES sets(set_id)
    );
    """)
    print("Created or verified 'cards' table.")
