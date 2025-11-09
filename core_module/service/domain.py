import os
import traceback
from datetime import datetime
from time import sleep

from core_module.service import api
from core_module.utils.file_utils import save_object_to_file, load_json_file, get_repo_root, get_api_response_cache_dir
from core_module.utils.util import generate_file_name_from_function_info, debug_print


def handle_cache_and_api(api_function, *args, delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    """
    Generalized function to handle caching, API calls, and `updated_date`.

    Args:
        api_function (callable): The API function to call if cache is not found.
        *args: Arguments to pass to the API call.
        delete_cache (bool): If True, deletes the existing cache before proceeding.
        use_cache_only (bool): If True, only returns data if it exists in the cache; otherwise returns None.
        cache_file_name (str, optional): Manually specify the cache file name. If None, it's auto-generated.
        use_network_only (bool): If True, bypasses the cache read and fetches directly from the network.

    Returns:
        dict or None: Cached or API-fetched data, or None if cache-only is used and no cache exists.
    """
    try:
        # Use the provided file name or generate one automatically.
        file_name = cache_file_name or generate_file_name_from_function_info()

        # Handle Cache Deletion
        if delete_cache:
            delete_cache_file(file_name)
            # If we are also in cache-only mode, there's nothing more to do.
            if use_cache_only:
                return None

        # Handle Cache Read (unless network is forced)
        if not use_network_only and not delete_cache:
            if cache := get_cache(file_name):
                cache = prepare_cache_with_updated_date(cache, file_name)
                return cache

        # Handle Cache-Only Failure
        # If we reach this point in cache-only mode, the cache was missed or deleted.
        if use_cache_only:
            debug_print(f"Cache-only mode: No cache found for '{file_name}'. Returning None.")
            return {"data": None}

        # Perform Network Call (if cache was missed or network was forced)
        print(f"Calling API for '{file_name}'...")
        data = api_function(*args)

        # Handle scenario where API data is empty or None
        if not data:
            data = {"data": None}  # Ensure there is always a `data` key

        # If API returns a list, wrap it in a dictionary
        elif isinstance(data, list):
            data = {"data": data}

        # Add updated_date before saving cache
        data['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_cache(file_name, data)

        return data

    except Exception as e:
        tb = traceback.format_exc()
        debug_print(f"An unexpected error occurred: {e}")
        debug_print(f"Traceback details:\n{tb}")
        return None



def prepare_cache_with_updated_date(cache, cache_file_name):
    """
    Ensures the 'updated_date' key is present in the cache data.
    If cache is a list, it wraps it in a dictionary with the 'data' key.
    If missing, adds it based on the file's last modification time.

    Args:
        cache (dict or list): The cached data.
        cache_file_name (str): The cache file name (used for fetching modification time).

    Returns:
        dict: The updated cache (with 'updated_date' key included).
    """
    cache_file_path = f"{get_api_response_cache_dir()}{cache_file_name}"
    if isinstance(cache, list):
        # Wrap the list in a dictionary if it's not already
        cache = {"data": cache}

    if 'updated_date' not in cache:
        if os.path.exists(cache_file_path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file_path))
            cache['updated_date'] = mod_time.strftime('%Y-%m-%d %H:%M:%S')  # File Modification Time
        else:
            cache['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fallback to now
        save_cache(cache_file_name, cache)

    return cache


def get_cache(cache_file_name):
    """
    Fetches the JSON cache from disk if it exists.

    Args:
        cache_file_name (str): The name of the cache file.

    Returns:
        dict or None: The cached data or None if the file doesn't exist.
    """
    cache_file = f"{get_api_response_cache_dir()}{cache_file_name}"
    return load_json_file(cache_file)


def save_cache(file_path, data):
    """
    Saves data to a JSON cache file.

    Args:
        file_path (str): The path of the file to save.
        data (dict): The data to save.
    """
    save_object_to_file(data, filename=file_path, directory=get_api_response_cache_dir(), overwrite=True)


def delete_cache_file(cache_file_name):
    """
    Deletes a specific cache file if it exists.

    Args:
        cache_file_name (str): The name of the cache file to delete.
    """
    cache_file_path = os.path.join(get_api_response_cache_dir(), cache_file_name)
    try:
        if os.path.exists(cache_file_path):
            os.remove(cache_file_path)
            debug_print(f"Successfully deleted cache file: {cache_file_path}")
    except OSError as e:
        debug_print(f"Error deleting cache file {cache_file_path}: {e}")


def get_all_sets(delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    cache_file_name = f"get_all_sets.json"
    return handle_cache_and_api(api.get_all_pokemon_sets, delete_cache=delete_cache, use_cache_only=use_cache_only, cache_file_name=cache_file_name, use_network_only=use_network_only)


def get_set_list(setId=0, delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    cache_file_name = f"get_set_list_setId={setId}.json"
    return handle_cache_and_api(api.get_all_cards_in_set, setId, delete_cache=delete_cache, use_cache_only=use_cache_only, cache_file_name=cache_file_name, use_network_only=use_network_only)


def get_card_prices(setId=0, delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    cache_file_name = f"get_card_prices_setId={setId}.json"
    return handle_cache_and_api(api.get_card_prices_of_set, setId, delete_cache=delete_cache, use_cache_only=use_cache_only, cache_file_name=cache_file_name, use_network_only=use_network_only)


def get_card_id_psa_pop(card_id=0, delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    cache_file_name = f"get_card_id_psa_pop_card_id={card_id}.json"
    return handle_cache_and_api(api.get_card_id_psa_pop, card_id, delete_cache=delete_cache, use_cache_only=use_cache_only, cache_file_name=cache_file_name, use_network_only=use_network_only)


def get_volume_of_transactions(card_id=0, delete_cache=False, use_cache_only=False, cache_file_name=None, use_network_only=False):
    cache_file_name = f"get_volume_of_transactions_card_id={card_id}.json"
    return handle_cache_and_api(api.get_volume_of_transactions, card_id, delete_cache=delete_cache, use_cache_only=use_cache_only, cache_file_name=cache_file_name, use_network_only=use_network_only)


if __name__ == '__main__':
    # Example of using cache-only mode:
    # cached_data = get_card_id_psa_pop(76496, use_cache_only=True)
    # if cached_data:
    #     print("Successfully loaded from cache.")
    # else:
    #     print("No cache found.")

    # Example of forcing a cache deletion:
    # get_card_id_psa_pop(76496, delete_cache=True)

    # Example of manually specifying a cache file name
    # get_card_id_psa_pop(76496, cache_file_name="my_custom_cache_name.json")

    get_card_id_psa_pop(76496)
