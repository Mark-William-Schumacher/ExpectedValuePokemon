import json
import sqlite3
from datetime import datetime

from bs4 import BeautifulSoup

from web.backend.containers import AppContainer
from web.backend.db.util.manually_enter_in_psa_pop_report import add_manual_psa_pop


def parse_psa_pop_from_html(html_content, card_numbers_to_find):
    """
    Parses HTML content to find PSA population data for a list of card numbers.

    :param html_content: The HTML content as a string.
    :param card_numbers_to_find: A list of card numbers (e.g., "1/165") to look for.
    :return: A dictionary mapping card numbers to their population data.
             Example: {"1/165": {"psa_10_pop": 100, "total_pop": 500}}
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    results = {}

    table = soup.find('table', id='tablePSA')
    if not table:
        print("Error: Table with id 'tablePSA' not found.")
        return results

    rows = table.find_all('tr', role='row')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 1:
            # The card number is in the second cell
            card_number_cell = cells[1]
            card_number = card_number_cell.get_text(strip=True)

            if card_number in card_numbers_to_find:
                try:
                    # PSA 10 population is in the second to last cell's top div
                    psa_10_pop_cell = cells[-2]
                    psa_10_pop = int(psa_10_pop_cell.find('div').get_text(strip=True).replace(',', ''))

                    # Total population is in the last cell's first div
                    total_pop_cell = cells[-1]
                    total_pop = int(total_pop_cell.find('div').get_text(strip=True).replace(',', ''))

                    results[card_number] = {
                        "psa_10_pop": psa_10_pop,
                        "total_pop": total_pop
                    }
                except (ValueError, AttributeError) as e:
                    print(f"Could not parse population data for card number {card_number}: {e}")

    return results

def get_card_num_to_id_map(conn, card_ids, set_id):
    """
    Fetches card data and returns a mapping from card number (num) to card_id
    for a given list of card IDs and a specific set_id.
    """
    if not card_ids:
        return {}
    placeholders = ','.join('?' for _ in card_ids)
    query = f"SELECT num, card_id FROM cards WHERE card_id IN ({placeholders}) AND set_id = ?"
    cursor = conn.cursor()
    params = card_ids + [set_id]
    cursor.execute(query, params)
    return {row[0]: row[1] for row in cursor.fetchall()}


if __name__ == '__main__':

    container = AppContainer()
    container.wire(modules=[__name__])
    db = container.database()
    psa_dao = container.psa_dao()  # Get an instance of PsaDAO

    missing_pop_ids = [
        79841, 74035, 72744, 68459, 67186, 67094, 57668, 42914, 41550, 40476, 40343, 40200, 40115, 40114, 40112, 40108,
         40105, 40101, 40099, 40097, 40096, 40092, 40091, 40090, 40079, 40072, 40071, 40069, 40067, 40065, 17245, 16061,
         15871, 15090, 15053, 14926, 11586, 11425, 10445, 9552, 9551, 3844
    ]
    set_id = 174
    html_file_path = 'assets/psa_pop_cencus_2017_black_star_promo.html'

    # --- Database Connection and Query ---
    conn = db.get_connection()
    card_num_to_id_map = get_card_num_to_id_map(conn, missing_pop_ids, set_id)

    card_numbers_to_search = list(card_num_to_id_map.keys())
    print(f"Found {len(card_numbers_to_search)} card numbers to search for in the HTML.")


    # --- File Reading ---
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: HTML file not found at {html_file_path}")
        html_content = ""


    # --- Parsing ---
    if html_content:
        # Here, you would pass the `card_numbers` list fetched from the database.
        # We use our placeholder list for this example.
        population_data = parse_psa_pop_from_html(html_content, card_numbers_to_search)

        # --- Output ---
        if population_data:
            print("\n--- Inserting data via PSA DAO ---")
            for card_num, data in population_data.items():
                card_id = card_num_to_id_map.get(card_num)
                if not card_id:
                    print(f"Warning: No card_id found for card number {card_num}. Skipping.")
                    continue

                psa_10_pop = data.get('psa_10_pop', 0)
                total_pop = data.get('total_pop', 0)
                non_psa_10_pop = total_pop - psa_10_pop

                # Use the imported function to handle the logic
                add_manual_psa_pop(
                    psa_dao=psa_dao,
                    card_id=card_id,
                    psa_10_pop=psa_10_pop,
                    total_pop=total_pop
                )

    else:
            print("No matching cards found in HTML or data could not be extracted.")

