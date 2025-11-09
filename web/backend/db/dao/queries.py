# This file centralizes all raw SQL queries for the DAOs.
# This approach helps to:
#  1. Separate SQL logic from Python application logic.
#  2. Improve readability of the DAO methods.
#  3. Make queries easier to find, maintain, and reuse.

# --- INSERT / UPDATE Queries ---
UPSERT_CARD_SALES = "INSERT OR IGNORE INTO card_sales (card_id) VALUES (?)"
UPDATE_CARD_SALES_DATE = "UPDATE card_sales SET updated_date = ? WHERE card_id = ?"

BULK_INSERT_EBAY_AVG = """
    INSERT OR IGNORE INTO ebay_avg
    (card_id, date_sold, psa_grade, sold_price, volume)
    VALUES (?, ?, ?, ?, ?)
"""

BULK_INSERT_TCGPLAYER = """
    INSERT OR IGNORE INTO tcgplayer
    (source_tcgplayer_id, card_id, created_at, date_sold, interpolated, set_id, sold_price)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

BULK_INSERT_TRANSACTIONS = """
    INSERT OR IGNORE INTO transactions
    (source_transaction_id, card_id, date_sold, ebay_handle, ebay_item_id,
     marketplace, num_bids, psa_grade, set_id, sold_price, title)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

# --- SELECT Queries ---
SELECT_CARD_SALES_BY_ID = "SELECT * FROM card_sales WHERE card_id = ?"
SELECT_EBAY_AVG_BY_ID = "SELECT * FROM ebay_avg WHERE card_id = ?"
SELECT_TCGPLAYER_BY_ID = "SELECT * FROM tcgplayer WHERE card_id = ?"
SELECT_TRANSACTIONS_BY_ID = "SELECT * FROM transactions WHERE card_id = ?"
