def create_psa_population_table(cursor):
    """
    Creates the 'psa_population' table to store PSA grading population data for each card.

    - Each record is linked to a specific card via the 'card_id' foreign key.
    - A composite UNIQUE constraint on ('card_id', 'psa_grade') ensures that there
      is only one population count entry per grade for any given card.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS psa_population (
        psa_population_id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        psa_grade DECIMAL(3,1) NOT NULL,
        population_count INTEGER,
        updated_date DATETIME,
        FOREIGN KEY (card_id) REFERENCES cards(card_id),
        UNIQUE(card_id, psa_grade)
    );
    """)
    print("Created or verified 'psa_population' table.")
