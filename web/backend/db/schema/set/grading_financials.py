def create_grading_financials_table(cursor):
    """
    Creates the 'grading_financials' table to store calculated financial metrics
    related to the profitability of grading a card.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grading_financials (
        card_id INTEGER PRIMARY KEY,
        net_gain REAL,
        lucrative_factor REAL,
        total_cost REAL,
        expected_value REAL,
        last_calculated DATETIME,
        FOREIGN KEY (card_id) REFERENCES cards(card_id)
    );
    """)
    print("Created or verified 'grading_financials' table.")
