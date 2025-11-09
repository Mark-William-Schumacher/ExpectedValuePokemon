import os
import json
import sys

from core_module.utils.file_utils import get_api_response_cache_dir
from web.backend.config import CACHE_DIR
from web.backend.db.dao.candidates_dao import CandidatesDAO
from web.backend.db.dao.psa_dao import PsaDAO
from web.backend.db.dao.sales_dao import SalesDAO

# This adds the project root to the Python path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


def populate_sets(set_dao, cache_directory):
    """
    Scans a given cache directory and uses a provided DAO to populate the database.

    :param set_dao: A data access object with an `add_set_from_json` method.
    :param cache_directory: The path to the directory containing cache files.
    """
    if not os.path.isdir(cache_directory):
        print(f"Error: Cache directory not found at '{cache_directory}'.")
        return

    print(f"Scanning for set price files in: {cache_directory}\n")

    prefix_to_find = "get_card_prices_setId="
    for filename in sorted(os.listdir(cache_directory)):
        if filename.startswith(prefix_to_find) and filename.endswith('.json'):
            file_path = os.path.join(cache_directory, filename)
            print(f"--- Processing file: {filename} ---")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if not data.get('data'):
                    print(f"  - Warning: Skipping due to missing or empty 'data' key.")
                    continue

                # Use the injected DAO
                set_dao.add_set_from_json(data)
                print(f"  - Successfully processed and added to the database.")

            except json.JSONDecodeError:
                print(f"  - Error: Could not decode JSON. The file might be corrupt.")
            except Exception as e:
                print(f"  - An unexpected error occurred: {e}")


def populate_set_details(set_dao, cache_directory):
    """
    Populates the database with set details from 'get_all_sets.json'.

    :param set_dao: A data access object with an `add_set_details_from_json` method.
    :param cache_directory: The path to the directory containing the cache file.
    """
    set_details_file = "get_all_sets.json"
    file_path = os.path.join(cache_directory, set_details_file)

    if not os.path.exists(file_path):
        print(f"Warning: Set details file not found at '{file_path}'. Skipping.")
        return

    print(f"\n--- Processing file: {set_details_file} ---")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data.get('data'):
            print(f"  - Warning: Skipping due to missing or empty 'data' key.")
            return

        # Use the injected DAO to add set details
        set_dao.add_set_details_from_json(data)
        print(f"  - Successfully processed and added set details to the database.")

    except json.JSONDecodeError:
        print(f"  - Error: Could not decode JSON. The file might be corrupt.")
    except Exception as e:
        print(f"  - An unexpected error occurred: {e}")


def populate_sales_data(sales_dao, cache_directory):
    """
    Scans a given cache directory for sales transaction files and uses a
    provided DAO to populate the database.

    :param sales_dao: A data access object with an `add_sales_from_json` method.
    :param cache_directory: The path to the directory containing cache files.
    """
    if not os.path.isdir(cache_directory):
        print(f"Error: Cache directory not found at '{cache_directory}'.")
        return

    print(f"\nScanning for sales transaction files in: {cache_directory}\n")

    prefix_to_find = "get_volume_of_transactions_card_id="
    for filename in sorted(os.listdir(cache_directory)):
        if filename.startswith(prefix_to_find) and filename.endswith('.json'):
            file_path = os.path.join(cache_directory, filename)
            print(f"--- Processing file: {filename} ---")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # The sales_dao's add_sales_from_json handles cases with no data internally
                sales_dao.add_sales_from_json(data)
                print(f"  - Successfully processed and added to the database.")

            except json.JSONDecodeError:
                print(f"  - Error: Could not decode JSON. The file might be corrupt.")
            except Exception as e:
                print(f"  - An unexpected error occurred: {e}")

def populate_psa_data(psa_dao, cache_directory):
    """
    Scans a given cache directory for PSA population files and uses a
    provided DAO to populate the database.

    :param psa_dao: A data access object with an `add_psa_population_from_json` method.
    :param cache_directory: The path to the directory containing cache files.
    """
    if not os.path.isdir(cache_directory):
        print(f"Error: Cache directory not found at '{cache_directory}'.")
        return

    print(f"\nScanning for PSA population files in: {cache_directory}\n")

    prefix = "get_card_id_psa_pop_card_id="
    for filename in sorted(os.listdir(cache_directory)):
        if filename.startswith(prefix) and filename.endswith('.json'):
            file_path = os.path.join(cache_directory, filename)
            print(f"--- Processing file: {filename} ---")

            try:
                # Extract card_id from filename
                card_id_str = filename[len(prefix):-len('.json')]
                card_id = int(card_id_str)

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                psa_dao.add_psa_population_from_json(card_id, data)
                print(f"  - Successfully processed and added to the database for card_id {card_id}.")

            except ValueError:
                print(f"  - Error: Could not parse card_id from filename '{filename}'.")
            except json.JSONDecodeError:
                print(f"  - Error: Could not decode JSON. The file might be corrupt.")
            except Exception as e:
                print(f"  - An unexpected error occurred: {e}")



def populate_card_analytics_from_db(psa_dao: PsaDAO):
    """
    Backfills the 'card_analytics' table by calculating analytics for all
    cards that have existing data in the 'psa_population' table.
    """
    print("\n--- Backfilling Card Analytics Table ---")
    cursor = psa_dao.conn.cursor()

    # 1. Get all unique card IDs that have population data
    cursor.execute("SELECT DISTINCT card_id FROM psa_population")
    all_card_ids = [row[0] for row in cursor.fetchall()]

    if not all_card_ids:
        print("No cards with population data found to analyze.")
        return

    print(f"Found {len(all_card_ids)} cards to analyze. Starting process...")

    # 2. Iterate and update analytics for each card
    for i, card_id in enumerate(all_card_ids, 1):
        try:
            # This method already contains all the logic to calculate and save.
            # We run it in silent mode to allow for a clean progress indicator.
            psa_dao.update_card_analytics(card_id, silent=True)
            print(f"\r({i}/{len(all_card_ids)}) cards processed", end="", flush=True)
        except Exception as e:
            # Print a newline to avoid overwriting the progress bar
            print(f"\n({i}/{len(all_card_ids)}) Failed to process card_id {card_id}: {e}")

    print("\n--- Card Analytics backfill complete. ---")




def populate_grading_financials_from_db(candidates_dao: CandidatesDAO):
    """
    Backfills the 'grading_financials' table by calculating financial metrics
    for all cards in the database.
    """
    print("\n--- Backfilling Grading Financials Table ---")
    cursor = candidates_dao.conn.cursor()

    # Get all card IDs from the main cards table
    cursor.execute("SELECT card_id FROM cards")
    all_card_ids = [row[0] for row in cursor.fetchall()]

    if not all_card_ids:
        print("No cards found in the database to analyze.")
        return

    print(f"Found {len(all_card_ids)} cards to analyze. Starting financial calculation...")

    # Iterate and update financial metrics for each card
    for i, card_id in enumerate(all_card_ids, 1):
        try:
            candidates_dao.update_grading_financials(card_id)
            # The print statement is inside the DAO method, so we don't need one here.
            print(f"\r({i}/{len(all_card_ids)}) cards processed", end="", flush=True)
        except Exception as e:
            print(f"\n({i}/{len(all_card_ids)}) Failed to process financials for card_id {card_id}: {e}")

    print("\n--- Grading Financials backfill complete. ---")



def populate_sales_volume_from_db(sales_dao: SalesDAO):
    """
    Backfills the 'sales_volume' table by calculating sales volumes for all
    cards that have transaction data.
    """
    print("\n--- Backfilling Sales Volume Table ---")
    cursor = sales_dao.conn.cursor()

    # Get all unique card IDs that have transactions
    cursor.execute("SELECT DISTINCT card_id FROM transactions")
    all_card_ids = [row[0] for row in cursor.fetchall()]

    if not all_card_ids:
        print("No cards with transaction data found to analyze.")
        return

    print(f"Found {len(all_card_ids)} cards to analyze. Starting sales volume calculation...")

    # Iterate and update sales volume for each card
    for i, card_id in enumerate(all_card_ids, 1):
        try:
            sales_dao.update_sales_volume(card_id)
            print(f"\r({i}/{len(all_card_ids)}) cards processed", end="", flush=True)
        except Exception as e:
            print(f"\n({i}/{len(all_card_ids)}) Failed to process sales volume for card_id {card_id}: {e}")

    print("\n--- Sales Volume backfill complete. ---")


"""
This is run to create a fresh instance of the database with cached jsons
"""
def cache_jsons_to_db():
    # 2. Get the DAO instance from the container.

    # 3. Inject the DAO instance and path into the core logic.
    populate_sets(
        set_dao=set_dao_instance,
        cache_directory=CACHE_DIR
    )

    print("\nFinished populating all sets from the cache.")

    # Also populate set details
    populate_set_details(
        set_dao=set_dao_instance,
        cache_directory=CACHE_DIR
    )

    # Also populate sales data
    populate_sales_data(
        sales_dao=sales_dao_instance,
        cache_directory=CACHE_DIR
    )

    # Also populate PSA data
    populate_psa_data(
        psa_dao=psa_dao_instance,
        cache_directory=CACHE_DIR
    )

if __name__ == '__main__':
    # Now we can import the container
    from web.backend.containers import AppContainer
    # 1. Create an instance of the application's DI container.
    container = AppContainer()
    # This wires up the container's lifecycle to the application's scope.
    # For a script, we do this manually.
    container.wire(modules=[__name__])

    try:
        set_dao_instance = container.set_dao()
        sales_dao_instance = container.sales_dao()
        psa_dao_instance = container.psa_dao()
        candidates_dao_instance = container.candidates_dao()

        """ Only run this if you want to populate the database with cached jsons"""
        # cache_jsons_to_db()

        # populate_card_analytics_from_db(psa_dao_instance)
        # populate_grading_financials_from_db(candidates_dao_instance)
        populate_sales_volume_from_db(sales_dao_instance)



    finally:
        # 4. Shut down the container. This automatically calls .close_connection()
        # on the database provider because we wrapped it in a Closing provider.
        container.shutdown_resources()
