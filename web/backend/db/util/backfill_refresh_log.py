import sqlite3
from web.backend.containers import AppContainer
from web.backend.db.dao.candidates_dao import CandidatesDAO

def check_for_pending_updates(candidates_dao: CandidatesDAO):
    """
    Checks and prints the number of cards that are currently pending a sales volume update.
    """
    # We check for cards that haven't been attempted in the last 0 days.
    # This will find any card that is missing from the log table.
    pending_cards = candidates_dao.find_profitable_candidates_without_sales_volume(20, 70, days_since_last_attempt=0)
    if pending_cards:
        print(f"Found {len(pending_cards)} cards that are pending a sales volume update.")
    else:
        print("Verification successful: No cards are currently pending a sales volume update.")


def backfill_sales_volume_refresh_log():
    """
    Backfills the 'sales_volume_refresh_log' table for all existing cards,
    setting their 'last_attempted_date' to 10 days ago.

    This ensures that the system can attempt to refresh sales data for all
    cards after this script is run.
    """
    print("\n--- Starting backfill for sales_volume_refresh_log ---")

    # Setup DI container to get a database connection
    container = AppContainer()
    db = container.database()
    conn = db.get_connection()
    candidates_dao = CandidatesDAO(conn)

    try:
        # --- Verification Step 1: Check before backfill ---
        print("\n--- Verifying pending updates before backfill ---")
        check_for_pending_updates(candidates_dao)

        # Get all unique card IDs from the main cards table
        cursor = conn.cursor()
        cursor.execute("SELECT card_id FROM cards")
        all_card_ids = [row[0] for row in cursor.fetchall()]

        if not all_card_ids:
            print("No cards found in the 'cards' table. Nothing to backfill.")
            return

        print(f"\nFound {len(all_card_ids)} cards to backfill. Preparing to insert/update...")

        # This query will either insert a new row or replace an existing one for each card_id,
        # setting the date to 10 days ago using SQLite's date function.
        backfill_query = """
            INSERT OR REPLACE INTO sales_volume_refresh_log (card_id, last_attempted_date)
            VALUES (?, date('now', '-10 days'));
        """

        # Prepare the data for executemany
        data_to_insert = [(card_id,) for card_id in all_card_ids]

        # Execute the query for all cards in a single batch
        cursor.executemany(backfill_query, data_to_insert)
        conn.commit()

        print(f"\nSuccessfully backfilled 'sales_volume_refresh_log' for {cursor.rowcount} cards.")
        print("All cards are now set with a 'last_attempted_date' of 10 days ago.")

        # --- Verification Step 2: Check after backfill ---
        print("\n--- Verifying pending updates after backfill ---")
        check_for_pending_updates(candidates_dao)

    except sqlite3.Error as e:
        print(f"\nAn error occurred during the backfill: {e}")
        conn.rollback()
    finally:
        # The container's resource management should handle closing the connection
        pass

if __name__ == '__main__':
    backfill_sales_volume_refresh_log()