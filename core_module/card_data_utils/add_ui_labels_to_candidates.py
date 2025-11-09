# Helper function to format dates
from datetime import datetime

from core_module.card_data_utils.exchangeRate import USD_TO_CAD_EXCHANGE_RATE
from core_module.utils.util import debug_print
from core_module.utils.file_utils import load_json_file

def format_date(date_str):
    """Convert date string to the format 'Month Day, Year'."""
    try:
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')  # Parse the date string
        return date_obj.strftime('%b %d, %Y')  # Format as 'Month Day, Year'
    except ValueError:
        return date_str  # Return original string if parsing fails


def add_ui_labels_to_candidates_json(candidates_object):
    # Process each card's sales data to format the date
    candidates_object = convert_to_cad(candidates_object)
    candidates_object = get_recent_sales_ui(candidates_object)
    # for card in candidates_object:
    #     card["raw_price"] = card["average_sold_price"]
    return candidates_object


# Convert USD to CAD in required fields
def convert_to_cad(data):
    for card in data:
        # Convert `raw_price`, `total_cost`, `net_gain`
        card["raw_price_cad_label"] = round(card["raw_price"] * USD_TO_CAD_EXCHANGE_RATE, 2)
        card["psa_10_price_cad_label"] = round(card["psa_10_price"] * USD_TO_CAD_EXCHANGE_RATE, 2)

        # Convert `sold_price` in `recent_raw_ebay_sales`
        sales = card.get("recent_raw_ebay_sales", [])
        for sale in sales:
            sale["sold_price_cad_label"] = round(sale["sold_price"] * USD_TO_CAD_EXCHANGE_RATE, 2)

        # Convert `avg` in `stats` within `card_data`
        for stat in card["card_data"]["stats"]:
            stat["avg_cad_label"] = round(stat["avg"] * USD_TO_CAD_EXCHANGE_RATE, 2)

    return data



def get_recent_sales_ui(candidates_object):
    for card in candidates_object:
        average_price = 0
        try:
            # Parse the sales and remove the highest and lowest sold_price first.
            sales = card.get("recent_raw_ebay_sales", [])

            # Remove the highest and lowest sold_price.
            filtered_sales = sorted(sales, key=lambda sale: sale["sold_price"])[2:-1]

            # Sort the remaining sales based on the "date_sold" field.
            sorted_sales_by_date = sorted(
                filtered_sales,
                key=lambda x: datetime.strptime(x["date_sold"], "%a, %d %b %Y %H:%M:%S %Z"),
                reverse=True  # Most recent date first.
            )

            # Calculate the average sold_price.
            if sorted_sales_by_date:
                average_price = sum(sale['sold_price'] for sale in sorted_sales_by_date) / len(
                    sorted_sales_by_date)

            card["average_sold_price"] = average_price

            # Format the sales details with short month names.
            sales_details = [
                f"{datetime.strptime(sale['date_sold'], '%a, %d %b %Y %H:%M:%S %Z').strftime('%b %d, %Y')}: "
                f"${sale['sold_price']:.2f} CAD"
                for sale in sorted_sales_by_date
            ]
            card["sales_details_ui"] = sales_details
        except ValueError as e:
            sales_details = "Date format error. Unable to parse some dates."
            debug_print(f"Error parsing dates: {e}")

    return candidates_object

if __name__ == '__main__':
    candidates = load_json_file("cache/candidates.json")
    add_ui_labels_to_candidates_json(candidates)
    print(
        f"Added UI labels to {len(candidates)} candidates. "
        f"Raw price: {candidates[0]['raw_price']:.2f} CAD, Average sold price: {candidates[0]['average_sold_price']:.2f} CAD"
    )