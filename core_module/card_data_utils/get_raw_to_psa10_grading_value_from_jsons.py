from core_module.card_data_utils.get_target_sets import get_target_set_ids
from core_module.service.domain import get_card_prices


def get_card_values(card):
    stats = card["stats"]  # Access the stats array
    raw_value = None
    psa_10_value = None
    for stat in stats:
        if stat.get("source") == 0.0:  # Check if source is 0
            raw_value = stat.get("avg")  # Get the avg value
        if stat.get("source") == 10.0:  # Check if source is 0
            psa_10_value = stat.get("avg")  # Get the avg value
    return (raw_value, psa_10_value)


def get_set_candidates(set_id=0):
    candidates = []
    data = get_card_prices(set_id)
    if data is None or data.get("data") is None:
        return candidates
    data = data.get("data")
    for card in data:
        raw, psa_10 = get_card_values(card)
        if raw is not None and psa_10 is not None:
            if psa_10 > raw + 70 and psa_10 > 120:
                candidate = {
                    'name': card["name"],
                    'raw_price': raw,
                    'psa_10_price': psa_10,
                    'id': card["id"],
                    'set_code': card["set_code"],
                    'stats_url': card["stat_url"],
                    'release_date': card["release_date"],
                    'set_name': card["set_name"],
                    'set_id': card["set_id"],
                    'card_data': card
                }
                candidates.append(candidate)
                # debug_print(card["name"], card["id"])
    return candidates

def get_raw_to_psa10_grading_value_from_jsons_cache():
    candidates = []
    for set in get_target_set_ids():
        candidates.extend(get_set_candidates(set))
    return candidates