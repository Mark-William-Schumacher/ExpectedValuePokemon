import json
from datetime import datetime

from web.backend.containers import AppContainer


def add_manual_psa_pop(psa_dao, card_id, psa_10_pop, total_pop):
    """
    Constructs a JSON object for PSA population and adds it to the database via the PsaDAO.

    :param psa_dao: An instance of the PsaDAO.
    :param card_id: The ID of the card to update.
    :param psa_10_pop: The population count for PSA 10 grade.
    :param total_pop: The total population count for the card.
    """
    if card_id is None or psa_10_pop is None or total_pop is None:
        print("Error: card_id, psa_10_pop, and total_pop must be provided.")
        return

    non_psa_10_pop = total_pop - psa_10_pop
    if non_psa_10_pop < 0:
        print(f"Error: total_pop ({total_pop}) cannot be less than psa_10_pop ({psa_10_pop}).")
        return

    # Construct the JSON in the specified format
    output_json = {
        "9.0": non_psa_10_pop,  # Assuming the remainder goes to grade 9.0 for simplicity
        "10.0": psa_10_pop,
        "updated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    print(f"--- Preparing to update Card ID: {card_id} ---")
    print("Generated JSON:")
    print(json.dumps(output_json, indent=4))

    try:
        print(f"\nAdding/updating PSA population data for card_id: {card_id}")
        psa_dao.add_psa_population_from_json(card_id, output_json)
        print(f"Successfully updated card_id: {card_id}")
    except Exception as e:
        print(f"  Error inserting data for card_id {card_id}: {e}")


if __name__ == '__main__':
    # --- Configuration ---
    # MODIFY THE VALUES BELOW
    CARD_ID_TO_UPDATE = 40200      # <--- Replace with the target card_id
    PSA_10_POPULATION = 		83       # <--- Replace with the PSA 10 population
    TOTAL_POPULATION = 1730        # <--- Replace with the total population

    # --- Script Execution ---
    container = AppContainer()
    try:
        container.wire(modules=[__name__])
        psa_dao_instance = container.psa_dao()

        add_manual_psa_pop(
            psa_dao=psa_dao_instance,
            card_id=CARD_ID_TO_UPDATE,
            psa_10_pop=PSA_10_POPULATION,
            total_pop=TOTAL_POPULATION
        )
    finally:
        container.shutdown_resources()
        print("\nScript finished.")
