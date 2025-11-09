from datetime import datetime
from collections import defaultdict
from itertools import groupby
from operator import itemgetter


def filter_cards(cards,
                 gem_rate=0.40,
                 net_gain=20,
                 total_cost=500,
                 lucrative_factor=0.50,
                 psa10_volume=15,
                 start_date="2014-02-01",
                 end_date=None):
    """
    Filters cards based on specified parameters with defaults.

    Args:
        cards (list): List of card dictionaries to filter.
        gem_rate (float): Minimum gem rate (default=0.40).
        net_gain (int): Minimum net gain (default=20).
        total_cost (int): Maximum total cost (default=500).
        lucrative_factor (float): Minimum lucrative factor (default=0.50).
        psa10_volume (int): Minimum PSA 10 volume (default=15).
        start_date (str): Release date filter (only include cards with release_date after this date).

    Returns:
        list: Flattened list of filtered cards.
    """
    start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

    # Apply initial sorting by release_date (ascending) and then by lucrative_factor (descending)
    sorted_cards = sorted(
        cards,
        key=lambda x: (x["release_date"], -x["lucrative_factor"])
    )

    # Group cards by release_date
    grouped_cards = {
        release_date: list(cards) for release_date, cards in groupby(sorted_cards, key=itemgetter("release_date"))
    }

    # Apply filtering with dynamic parameters
    filtered_cards = {
        release_date: [
            card for card in cards
            if (
                   # Ensure release_date is after the target_date
                       datetime.strptime(card["release_date"], "%Y-%m-%d") > start_date_parsed and
                       (end_date_parsed is None or datetime.strptime(card["release_date"],
                                                                     "%Y-%m-%d") <= end_date_parsed)

               ) and (
                   # Additional filtering conditions based on function arguments
                       card["gem_rate"] >= gem_rate
                       and card["net_gain"] >= net_gain
                       and card["total_cost"] <= total_cost
                       and card["lucrative_factor"] > lucrative_factor
                       and card["psa10_volume"] > psa10_volume
               )
        ]
        for release_date, cards in grouped_cards.items()
    }

    # Flatten out the grouped filtered results for final output
    flat_filtered_cards = [
        card for group in filtered_cards.values() for card in group
    ]

    return flat_filtered_cards
