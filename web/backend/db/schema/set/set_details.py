def create_set_details_table(cursor):
    """
    Creates the 'set_details' table to store additional, separately-sourced
    information about each card set. The 'set_id' acts as both the primary
    key and a foreign key to the 'sets' table, enforcing a one-to-one
    relationship.
    """
    cursor.execute("""
       CREATE TABLE IF NOT EXISTS set_details (
        set_id INTEGER PRIMARY KEY,
        language TEXT,
        release_date DATETIME,
        updated_date DATETIME,
        FOREIGN KEY (set_id) REFERENCES sets(set_id)
    );
    """)
    print("Created or verified 'set_details' table.")
