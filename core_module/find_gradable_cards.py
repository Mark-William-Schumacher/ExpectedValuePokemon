
from core_module.card_data_utils import get_target_sets
from core_module.card_data_utils.add_ui_labels_to_candidates import add_ui_labels_to_candidates_json
from core_module.card_data_utils.calculate_expected_value import calculate_net_gain
from core_module.card_data_utils.calculate_gem_rate import calculate_gem_rate
from core_module.card_data_utils.calculate_volume import calculate_volumes_last_month
from core_module.card_data_utils.get_raw_to_psa10_grading_value_from_jsons import \
    get_raw_to_psa10_grading_value_from_jsons_cache
from core_module.card_data_utils.get_recent_raw_ebay_sales import filter_recent_raw_ebay_sales
from core_module.card_data_utils.get_target_sets import get_target_set_ids
from core_module.service.domain import get_card_prices, get_volume_of_transactions, get_card_id_psa_pop
from core_module.utils.file_utils import save_object_to_file, load_json_file
from core_module.utils.util import debug_print


candidates = get_raw_to_psa10_grading_value_from_jsons_cache()

debug_print("len: ", len(candidates))

# for candidate in candidates:
#     debug_print(candidate["name"], candidate["psa10_volume"])

list_of_ids_no_pop_data = []
for candidate in candidates:
    population_data = get_card_id_psa_pop(candidate["id"], use_cache_only=True)
    if (population_data is None) or (population_data.get("data") is None):
        list_of_ids_no_pop_data.append(candidate['id'])
        debug_print(
            f"No population data found for card: {candidate['name']}, id: {candidate['id']}"
        )
    psa_10_pop, non_psa10_pop, gem_rate = calculate_gem_rate(population_data)
    candidate["psa_10_pop"] = psa_10_pop
    candidate["non_psa_10_pop"] = non_psa10_pop
    candidate["gem_rate"] = gem_rate
    debug_print(
        f"Card: {candidate['name']}, PSA 10: {candidate['psa_10_price']:.2f}, Population: {candidate['psa_10_pop']}"
    )


save_object_to_file(candidates, "candidates_temp.json")
# Convert to CAD
candidates = add_ui_labels_to_candidates_json(candidates)

for card in candidates:
    ev, total_cost, net_gain, lucrative_factor = calculate_net_gain(card, grading_cost=29)
    card["ev"] = ev
    card["total_cost"] = total_cost
    card["net_gain"] = net_gain
    card["lucrative_factor"] = lucrative_factor

before_removal_of_net_gain = len(candidates)

for candidate in candidates[:]:  # Create a copy of the list for iteration
    if candidate["net_gain"] < 0:
        debug_print("Removed: ", candidate["name"], candidate["net_gain"])
        candidates.remove(candidate)

after_removal_of_net_gain = len(candidates)


"""
Remove low volume cards
"""
for index, candidate in enumerate(candidates, start=1):
    volumeData = get_volume_of_transactions(candidate["id"], use_cache_only=True)
    psa10_volume, non_psa10_volume = calculate_volumes_last_month(volumeData)
    recent_raw_ebay_sales = filter_recent_raw_ebay_sales(volumeData)
    candidate["psa10_volume"] = psa10_volume
    candidate["non_psa10_volume"] = non_psa10_volume
    candidate["recent_raw_ebay_sales"] = recent_raw_ebay_sales

    # Print the current progress
    print(f"\r{index}/{len(candidates)} items processed", end="", flush=True)

    if psa10_volume == 0 and non_psa10_volume == 0:
        debug_print("No volume: ", candidate["name"], candidate["id"])

list_of_ids_no_volume = []
for candidate in candidates[:]:  # Create a copy of the list for iteration
    if ("psa10_volume" not in candidate
            and candidate["net_gain"] > 50
            and candidate["id"]
            and candidate["lucrative_factor"] > 0.6
            and candidate["total_cost"] < 200
    ) :
        list_of_ids_no_volume.append(candidate['id'])
        debug_print("added: ", candidate["name"])

debug_print("len: ", len(candidates))
before_removal_of_volume = len(candidates)
for candidate in candidates[:]:  # Create a copy of the list for iteration
    if not candidate["psa10_volume"] or candidate["psa10_volume"] < 7:
        debug_print("Removed: ", candidate["name"], candidate["psa10_volume"])
        candidates.remove(candidate)
after_removal_of_volume = len(candidates)

debug_print("Before removing net gain" , before_removal_of_net_gain)
debug_print("After removing net gain" , after_removal_of_net_gain)
debug_print("Before removing volume" , before_removal_of_volume)
debug_print("After removing volume" , after_removal_of_volume)

save_object_to_file(candidates, "candidates.json")
debug_print("length of total searchable cards", len(candidates))
list_of_ids_no_volume.sort()
debug_print("length of no volume data:",len(list_of_ids_no_volume))
debug_print("no volume data:", list_of_ids_no_volume)

list_of_ids_no_pop_data.sort()
debug_print("length of no pop data:", len(list_of_ids_no_pop_data))
debug_print("No pop card list" , list_of_ids_no_pop_data)


# candidates_
