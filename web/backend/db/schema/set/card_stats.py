def create_card_stats_table(cursor):
    """
    Creates the 'card_stats' table to store statistical data for each card.
    Each stat is linked to a card via the 'card_id' foreign key.
    A composite unique constraint on (card_id, source) prevents duplicate entries.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_stats (
        card_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER,
        avg REAL,
        source REAL,
        FOREIGN KEY (card_id) REFERENCES cards(card_id),
        UNIQUE(card_id, source)
    );
    """)
    print("Created or verified 'card_stats' table.")
