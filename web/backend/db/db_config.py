import sqlite3
from datetime import datetime

# A flag to ensure this setup logic runs only once per application instance.
_is_configured = False

def configure_sqlite_for_project():
    """
    Registers global adapters and converters for the sqlite3 library
    to handle project-specific data types, such as datetimes.

    This function is idempotent and can be safely called multiple times.
    """
    global _is_configured
    if _is_configured:
        return

    # --- Define the conversion functions ---

    # Adapter: Converts Python datetime objects to ISO 8601 strings for SQLite.
    def adapt_datetime_iso(dt):
        return dt.isoformat()

    # Converter: Parses ISO 8601 strings from SQLite back into Python datetime objects.
    def convert_datetime_iso(s):
        # The string from the database is bytes, so it needs to be decoded.
        return datetime.fromisoformat(s.decode('utf-8'))

    # --- Register the functions with the sqlite3 library ---
    sqlite3.register_adapter(datetime, adapt_datetime_iso)
    sqlite3.register_converter("DATETIME", convert_datetime_iso)

    _is_configured = True
