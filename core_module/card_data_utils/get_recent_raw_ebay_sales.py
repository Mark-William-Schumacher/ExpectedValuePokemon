from datetime import datetime
from pprint import pprint

from core_module.card_data_utils.exchangeRate import USD_TO_CAD_EXCHANGE_RATE
from core_module.service.api import get_volume_of_transactions
from core_module.utils.file_utils import load_json_file
from core_module.utils.util import debug_print


def filter_recent_raw_ebay_sales(data):
    """
    Filters transactions where the marketplace is 'ebay', psa_grade is 0.0,
    and returns up to 10 most recent transactions based on the 'date_sold'.

    Args:
        data (dict): A dictionary containing transaction data, or None.

    Returns:
        list: Filtered list of transactions up to 10 most recent ones.
    """
    if not data:
        return []
    transactions = data.get("transactions", [])

    # Filter transactions where marketplace is "ebay" and psa_grade is 0.0
    filtered_transactions = [
        txn for txn in transactions
        if txn["marketplace"] == "ebay" and txn["psa_grade"] == 0.0
    ]

    # Sort the filtered transactions by date_sold in descending order
    sorted_transactions = sorted(
        filtered_transactions,
        key=lambda txn: datetime.strptime(txn["date_sold"], "%a, %d %b %Y %H:%M:%S %Z"),
        reverse=True
    )

    # Add converted sold_price_cad field to each transaction
    for txn in sorted_transactions:
        # Ensure 'sold_price' field exists and isn't None
        if "sold_price" in txn and isinstance(txn["sold_price"], (int, float)):
            txn["sold_price_cad"] = txn["sold_price"] * USD_TO_CAD_EXCHANGE_RATE
        else:
            txn["sold_price_cad"] = None  # Handle missing or invalid sold_price

    # Return up to 10 most recent transactions
    return sorted_transactions[:10]


# Call the function
if __name__ == '__main__':
    # input_data = load_json_file("cache/api_responses/get_volume_of_transactions_card_id=17.json")
    input_data = get_volume_of_transactions(76783)
    # Call the function
    result = filter_recent_raw_ebay_sales(input_data)
    pprint(result)