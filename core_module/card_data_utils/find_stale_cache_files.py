import os
import json
from datetime import datetime, timedelta
from typing import List

# This assumes 'get_api_response_cache_dir' is in a file that can be imported.
# If this script is run as a standalone, you might need to adjust the path logic.
from core_module.utils.file_utils import get_api_response_cache_dir


def find_stale_cache_files() -> List[int]:
    """
    Scans the cache/api_responses directory for files starting with
    'get_card_prices_setId=' and identifies those that are stale or invalid.

    A file is considered stale if:
    - The 'updated_date' is older than two days.
    - The 'data' key is missing, null, or an empty list.
    - The file contains invalid JSON.

    Returns a list of unique integer set IDs for the stale files.
    """
    try:
        api_responses_dir = get_api_response_cache_dir()

        if not os.path.isdir(api_responses_dir):
            print(f"Error: Directory not found at '{api_responses_dir}'.")
            return []

        print(f"Scanning for stale or invalid files in: {api_responses_dir}\n")

        stale_set_ids = set()
        stale_file_details = []
        prefix_to_find = "get_card_prices_setId="
        two_days_ago = datetime.now() - timedelta(days=2)

        # Iterate over all files in the directory
        for filename in os.listdir(api_responses_dir):
            if filename.startswith(prefix_to_find) and filename.endswith('.json'):
                file_path = os.path.join(api_responses_dir, filename)
                is_stale = False
                reason = ""

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # --- Condition 1: Check for invalid or empty 'data' key ---
                    card_data = data.get('data')
                    if card_data is None:
                        is_stale = True
                        reason = "Missing or null 'data' key"
                    elif isinstance(card_data, list) and not card_data:
                        is_stale = True
                        reason = "Empty 'data' array"

                    # --- Condition 2: Check for stale 'updated_date' (only if data is valid) ---
                    if not is_stale:
                        updated_date_str = data.get('updated_date')
                        if updated_date_str:
                            updated_date = datetime.strptime(updated_date_str, '%Y-%m-%d %H:%M:%S')
                            if updated_date < two_days_ago:
                                is_stale = True
                                reason = f"Stale date: {updated_date.strftime('%Y-%m-%d')}"
                        else:
                            # A missing updated_date can also be considered stale.
                            is_stale = True
                            reason = "Missing 'updated_date' key"

                except json.JSONDecodeError:
                    is_stale = True
                    reason = "Invalid JSON"
                except Exception as e:
                    # Capture other file processing errors without crashing the whole scan
                    stale_file_details.append((filename, f"Unexpected error: {e}"))

                if is_stale:
                    stale_file_details.append((filename, reason))
                    try:
                        set_id_str = filename.removeprefix(prefix_to_find).removesuffix('.json')
                        stale_set_ids.add(int(set_id_str))
                    except ValueError:
                        print(f"Warning: Could not parse set ID from filename: {filename}")

        if not stale_file_details:
            print("No stale or invalid cache files were found.")
        else:
            print("--- Stale or Invalid Cache Files Found ---")
            # Sort by filename for a consistent and readable output
            for filename, reason in sorted(stale_file_details):
                print(f"- {filename} (Reason: {reason})")

        return sorted(list(stale_set_ids))

    except Exception as e:
        print(f"A general error occurred: {e}")
        return []


if __name__ == '__main__':
    stale_ids = find_stale_cache_files()
    if stale_ids:
        print("\n--- Stale Set IDs ---")
        print(f"Found {len(stale_ids)} stale set(s):")
        print(stale_ids)
