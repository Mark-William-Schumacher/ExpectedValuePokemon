from datetime import datetime
from dateutil.relativedelta import relativedelta

from core_module.service.domain import get_all_sets
from core_module.utils.file_utils import load_json_file
from core_module.utils.util import debug_print


def get_target_set_ids():
    Mega_Evolution_Promos = 575
    Mega_Evolution = 574
    White_Flare = 571
    Black_Bolt = 570
    Destined_Rivals = 567
    Journey_Together = 562
    Mcdonalds_Dragon_Discovery = 559
    Prismatic_Evolutions = 557
    Surging_Sparks = 555
    Stellar_Crown = 549
    Trick_or_Trade_2024 = 554
    Shrouded_Fable = 548
    Twilight_Masquerade = 545
    Temporal_Forces = 542
    Paldean_Fates = 539
    Trading_Card_Game_Classic = 561
    Paradox_Rift = 536
    Pokemon_Card_151 = 532
    Trick_or_Trade_2023 = 531
    Obsidian_Flames = 517
    McDonalds_Promos_2023 = 530
    Paldea_Evolved = 513
    Scarlet_Violet_Base = 510
    Crown_Zenith = 506
    Scarlet_Violet_Promos = 515
    Silver_Tempest = 503
    Lost_Origin = 400
    Trick_or_Trade_2022 = 504
    Mcdonalds_Promos_2022 = 399
    Pokemon_GO = 387
    Astral_Radiance = 182
    Brilliant_Stars = 178
    Fusion_Strike = 172
    Celebrations = 112
    Celebrations_Classic_Collection = 111
    Evolving_Skies = 108
    Chilling_Reign = 26
    Battle_Styles = 20
    Shining_Fates = 21
    Mcdonalds_25th_Anniversary = 171
    Vivid_Voltage = 3
    Champions_Path = 2
    Darkness_Ablaze = 4
    Rebel_Clash = 5
    Sword_Shield = 6
    Cosmic_Eclipse = 7
    McDonalds_Promos_2019 = 521
    Sword_Shield_Promo = 109
    Hidden_Fates = 1
    Unified_Minds = 8
    Unbroken_Bonds = 24
    Detective_Pikachu = 23
    Team_Up = 9
    Lost_Thunder = 10
    McDonalds_Promos_2018 = 522
    Dragon_Majesty = 11
    Celestial_Storm = 12
    Forbidden_Light = 13
    Ultra_Prism = 14
    Crimson_Invasion = 15
    Shining_Legends = 16
    Burning_Shadows = 17
    McDonalds_Promos_2017 = 523
    Guardians_Rising = 18
    Sun_Moon = 19
    Sun_Moon_Black_Star_Promo = 25
    Evolutions = 22
    McDonalds_Promos_2016 = 524
    Steam_Siege = 31
    Fates_Collide = 32
    Generations_Radiant_Collection = 169
    Generations = 33
    BREAKpoint = 34
    McDonalds_Promos_2015 = 525
    BREAKthrough = 35
    Ancient_Origins = 36
    Roaring_Skies = 37
    Double_Crisis = 291
    Primal_Clash = 38
    Phantom_Forces = 39
    Furious_Fists = 40
    Alternate_Art_Promos = 174
    McDonalds_Promos_2014 = 526
    Flashfire = 41
    XY_Base = 42
    Legendary_Treasures_Radiant_Collection = 170
    Legendary_Treasures = 43
    XY_Black_Star_Promos = 175
    Plasma_Blast = 44
    Plasma_Freeze = 45
    sets = [
        Mega_Evolution_Promos,
        Mega_Evolution,
        White_Flare,
        Black_Bolt,
        Destined_Rivals,
        Journey_Together,
        Mcdonalds_Dragon_Discovery,
        Prismatic_Evolutions,
        Surging_Sparks,
        Stellar_Crown,
        Trick_or_Trade_2024,
        Shrouded_Fable,
        Twilight_Masquerade,
        Temporal_Forces,
        Paldean_Fates,
        Trading_Card_Game_Classic,
        Paradox_Rift,
        Pokemon_Card_151,
        Trick_or_Trade_2023,
        Obsidian_Flames,
        McDonalds_Promos_2023,
        Paldea_Evolved,
        Scarlet_Violet_Base,
        Crown_Zenith,
        Scarlet_Violet_Promos,
        Silver_Tempest,
        Lost_Origin,
        Trick_or_Trade_2022,
        Mcdonalds_Promos_2022,
        Pokemon_GO,
        Astral_Radiance,
        Brilliant_Stars,
        Fusion_Strike,
        Celebrations,
        Celebrations_Classic_Collection,
        Evolving_Skies,
        Chilling_Reign,
        Battle_Styles,
        Shining_Fates,
        Mcdonalds_25th_Anniversary,
        Vivid_Voltage,
        Champions_Path,
        Darkness_Ablaze,
        Rebel_Clash,
        Sword_Shield,
        Cosmic_Eclipse,
        McDonalds_Promos_2019,
        Sword_Shield_Promo,
        Hidden_Fates,
        Unified_Minds,
        Unbroken_Bonds,
        Detective_Pikachu,
        Team_Up,
        Lost_Thunder,
        McDonalds_Promos_2018,
        Dragon_Majesty,
        Celestial_Storm,
        Forbidden_Light,
        Ultra_Prism,
        Crimson_Invasion,
        Shining_Legends,
        Burning_Shadows,
        McDonalds_Promos_2017,
        Guardians_Rising,
        Sun_Moon,
        Sun_Moon_Black_Star_Promo,
        Evolutions,
        McDonalds_Promos_2016,
        Steam_Siege,
        Fates_Collide,
        Generations_Radiant_Collection,
        Generations,
        BREAKpoint,
        McDonalds_Promos_2015,
        BREAKthrough,
        Ancient_Origins,
        Roaring_Skies,
        Double_Crisis,
        Primal_Clash,
        Phantom_Forces,
        Furious_Fists,
        Alternate_Art_Promos,
        McDonalds_Promos_2014,
        Flashfire,
        XY_Base,
        Legendary_Treasures_Radiant_Collection,
        Legendary_Treasures,
        XY_Black_Star_Promos,
        Plasma_Blast,
        Plasma_Freeze
    ]
    return sets


def check_release_date(cards):
    """
    Checks if the release date for each card in the list is within the range of 6 to 30 months ago,
    and formats the output in a specific way with sanitized names (removing spaces, apostrophes, '&', ':', and double underscores).

    Parameters:
        cards (list): List of dictionaries containing card data.

    Returns:
        tuple: A tuple with two elements -
               1. List of formatted strings containing card names and IDs.
               2. List of sanitized card names.
    """
    # Get today's date
    today = datetime.today()
    # Calculate the date range using relativedelta for accuracy
    todays_date = today
    one_twenty_month_ago = today - relativedelta(months=150)

    # Store formatted outputs
    formatted_cards = []
    set_names = []

    # Iterate over the list of cards
    for card in cards:
        # Extract and sanitize the release date
        release_date_str = card.get("release_date")
        if not release_date_str:
            debug_print(f"Release date missing for card ID {card['id']}. Skipping...")
            continue

        try:
            release_date = datetime.strptime(release_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            debug_print(f"Invalid date format for card ID {card['id']}. Skipping...")
            continue

        # Check if release date falls within the range
        if one_twenty_month_ago <= release_date <= todays_date:
            # Sanitize the name
            sanitized_name = (
                card.get("name", "Unknown")
                .replace(" ", "_")
                .replace("'", "")
                .replace("&", "")
                .replace(":", "")  # Remove colons
            )
            # Replace any occurrence of double underscores with a single underscore
            sanitized_name = sanitized_name.replace("__", "_")

            formatted_entry = f"{sanitized_name} = {card['id']}"
            formatted_cards.append(formatted_entry)
            set_names.append(sanitized_name)

    return formatted_cards, set_names


if __name__ == '__main__':
    # Load the card data
    data = get_all_sets(use_cache_only=True).get("data", [])
    formatted_cards, set_names = check_release_date(data)

    # Print the formatted output
    for entry in formatted_cards:
        print(entry)

    # Print the list of sets
    print("sets = [")
    print("    " + ",\n    ".join(set_names))
    print("]")
