from core_module.utils.util import debug_print
from core_module.utils.file_utils import load_json_file

def calculate_gem_rate(card_data):
    # Handle None or invalid input
    if not isinstance(card_data, dict):
        debug_print("Invalid card_data passed to calculate_gem_rate:", card_data)
        return 0, 0, 0  # Default values for PSA 10 population, others, and gem rate

    # Extract "10.0" count, ensuring it is an integer
    count_10 = card_data.get("10.0", 0) if isinstance(card_data.get("10.0", 0), int) else 0

    # Sum all values except "10.0", skipping keys where values are not int
    sum_except_10 = sum(
        value
        for key, value in card_data.items()
        if key != "10.0" and isinstance(value, int)
    )

    # Check for zero in the denominator
    denominator = sum_except_10 + count_10
    if denominator == 0:
        # Handle the edge case (e.g., return zero, or a value to indicate undefined gem rate)
        return count_10, sum_except_10, 0  # Assuming gem rate is 0 when denominator is 0

    # Calculate gem rate
    return count_10, sum_except_10, count_10 / denominator

if __name__ == '__main__':
    input_data = load_json_file("cache/api_responses/get_card_id_psa_pop_card_id=71601.json")
    debug_print("calculate_gem_rate", calculate_gem_rate(input_data))