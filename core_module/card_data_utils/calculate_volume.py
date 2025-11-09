from datetime import datetime, timezone, timedelta

from core_module.utils.util import debug_print
from core_module.utils.file_utils import load_json_file



def calculate_volumes_last_month(data):
    if not data:  # Check if data is valid
        return 0, 0  # Default to 0 volumes

    # Parse the `ebay_avg` list from the input JSON
    ebay_data = data.get("transactions", [])

    # Current date with timezone-aware UTC datetime
    today_date = datetime.now(timezone.utc)

    # Define the cutoff date (30 days ago)
    last_month_date = today_date - timedelta(days=30)

    # Initialize counters for PSA 10.0 and non-PSA 10.0
    psa10_volume_count = 0
    non_psa10_volume_count = 0

    # Iterate through each entry to calculate volumes
    for item in ebay_data:
        try:
            # Parse the date and ensure it's timezone-aware
            date_sold = datetime.strptime(item['date_sold'], "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue  # Skip invalid or missing dates

        # Check if the item has a valid `ebay_item_id` and falls within the last month
        if 'ebay_item_id' in item and date_sold >= last_month_date:
            if item.get('psa_grade') == 10.0:
                psa10_volume_count += 1
            else:
                non_psa10_volume_count += 1

    # Return the two counts
    return psa10_volume_count, non_psa10_volume_count


# Call the function
if __name__ == '__main__':
    input_data = load_json_file("cache/api_responses/get_volume_of_transactions_card_id=73104.json")
    # Call the function
    psa10_volume, non_psa10_volume = calculate_volumes_last_month(input_data)

    debug_print(f"Total volume for PSA 10 in the last month: {psa10_volume}")
    debug_print(f"Total volume for non-PSA 10 in the last month: {non_psa10_volume}")