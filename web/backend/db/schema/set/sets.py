def create_sets_table(cursor):
    """
    Creates the 'sets' table to store information about each card set.
    The 'set_id' is the natural primary key from the source data.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sets (
        set_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        code TEXT,
        updated_date DATETIME
    );
    """)
    print("Created or verified 'sets' table.")
