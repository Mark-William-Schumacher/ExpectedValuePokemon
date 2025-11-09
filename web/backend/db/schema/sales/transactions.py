from core_module.utils.file_utils import get_repo_root


def create_transactions_table(cursor):
    """
    Creates the 'transactions' table with a robust schema for storing sales data.

    This table uses a common database design pattern that includes both a
    surrogate primary key and natural keys from the source data.

    - Surrogate Key (`transaction_id`):
      This is the internal, auto-incrementing primary key for the table. Its
      sole purpose is to uniquely identify each row within our database. It provides
      a stable, controlled ID for linking to other tables (foreign keys).

    - Natural Keys (`source_transaction_id`, `ebay_item_id`):
      These keys come from the original source data (e.g., the API).
      `source_transaction_id` stores the 'id' from the JSON, and `ebay_item_id`
      stores the unique eBay listing ID. They are essential for:
        1. Idempotency: The `UNIQUE` constraint on these columns prevents
           inserting the same transaction multiple times.
        2. Traceability: They provide a reliable way to link a record back
           to its original entry in the source system for debugging or updates.



   --- Unique Values Found for 'marketplace' Key ---
  - eBay
  - ebay
    """

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_transaction_id INTEGER UNIQUE,
        card_id INTEGER,
        date_sold DATETIME,
        ebay_handle TEXT,
        ebay_item_id TEXT UNIQUE,
        marketplace TEXT,
        num_bids INTEGER,
        psa_grade DECIMAL(3,1),
        set_id INTEGER,
        sold_price DECIMAL(10,2),
        title TEXT,
        FOREIGN KEY (card_id) REFERENCES card_sales(card_id)
    );
    """)
    print("Created or verified 'transactions' table.")

