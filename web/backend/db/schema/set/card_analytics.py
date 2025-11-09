def create_card_analytics_table(cursor):
    """
    Creates the 'card_analytics' table to store derived metrics for cards,
    such as gem rate. This data is calculated from other tables like 'psa_population'.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_analytics (
        card_id INTEGER PRIMARY KEY,
        psa_10_pop INTEGER,
        non_psa_10_pop INTEGER,
        gem_rate REAL,
        last_calculated DATETIME,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)
    print("Created or verified 'card_analytics' table.")
