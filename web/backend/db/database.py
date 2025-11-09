import sqlite3
import os
from .database_setup import setup_schema

class Database:
    """
    A class to manage a connection to a SQLite database.
    It no longer manages its own singleton status; that is handled by the DI container.
    """
    def __init__(self, db_path: str):
        """
        Initializes the Database instance with a specific database file path,
        creates the connection, and ensures the database schema is set up.

        :param db_path: The full, absolute path to the database file.
        """
        print("Creating and setting up new Database instance...")
        self.db_path = db_path
        self.conn = None

        # Establish the connection immediately.
        try:
            # Ensure the parent directory exists.
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise  # Re-raise the exception to fail fast if the DB can't be opened.

        # Set up the schema right after connecting.
        if self.conn:
            print("Setting up database schema...")
            setup_schema(self.conn)
            print("Schema setup complete.")
        else:
            print("Warning: Database connection is not available. Schema setup skipped.")


    def get_connection(self):
        """Returns the active database connection."""
        return self.conn

    def shutdown(self):
        """Closes the database connection."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            print("Database connection closed.")
