import json
import os
import time
from datetime import datetime
from pprint import pprint
from string import ascii_lowercase

from core_module.utils.util import debug_print

def get_api_response_cache_dir():
    return f"{get_repo_root()}/cache/api_responses/"

def get_repo_root() -> str:
    """
    Dynamically finds the root directory of the repository by traversing upwards
    until it encounters a `.git` directory.

    Returns:
        str: Absolute path to the repository root.

    Raises:
        FileNotFoundError: If a `.git` directory is not found.
    """
    current_path = os.path.dirname(os.path.abspath(__file__))
    while current_path != os.path.dirname(current_path):  # Traverse upward
        if os.path.exists(os.path.join(current_path, ".git")):
            return current_path
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError("Repository root not found. Ensure a `.git` directory exists.")


def save_object_to_file(data, filename: str = None, directory: str = "cache", overwrite: bool = True):
    """
    Saves the provided data (dictionary or list of dictionaries) to a JSON file.
    Automatically removes old files before saving.

    Args:
        data (dict | list): Input data to save.
        filename (str, optional): Desired filename (auto-generated if not provided).
        directory (str, optional): Target directory for saving (default: "cache").
        overwrite (bool, optional): Allow overwriting of existing files (default: True).
    """
    remove_old_files(directory=directory)  # Clean up old files first

    if isinstance(data, dict):
        _save_dict_to_json(data, filename, directory, overwrite)
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        _save_list_of_dicts_to_json(data, filename, directory, overwrite)


def load_json_file(filepath: str) -> list | dict:
    """
    Loads and parses JSON from a specified file path (relative to repo root).

    Args:
        filepath (str): Path to the JSON file (relative to the repo root).

    Returns:
        list | dict: JSON data structured as a list of dictionaries or a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the JSON data is invalid.
    """
    # Resolve absolute filepath relative to the repository root
    repo_root = get_repo_root()
    absolute_filepath = os.path.join(repo_root, filepath)

    if not os.path.exists(absolute_filepath):
        debug_print(f"File not found: {absolute_filepath}")
        return None

    try:
        with open(absolute_filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        debug_print(f"Error decoding JSON file: {e}")
        return None


def remove_old_files(directory: str = "cache", days: int = 60) -> None:
    """
    Removes files older than the specified number of days from a directory.

    Args:
        directory (str): Target directory to clean (default: "cache").
        days (int): Number of days to use as the age threshold (default: 60).
    """
    directory = os.path.join(get_repo_root(), directory)
    if not os.path.exists(directory):
        debug_print(f"Directory '{directory}' does not exist. Nothing to clean.")
        return

    now = time.time()
    age_threshold = now - (days * 24 * 60 * 60)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and os.path.getmtime(filepath) < age_threshold:
            try:
                os.remove(filepath)
                debug_print(f"Removed old file: {filepath}")
            except OSError as e:
                debug_print(f"Error removing {filepath}: {e}")
    debug_print("Old file cleanup completed.")


def _save_dict_to_json(data: dict, filename: str = None, directory: str = "cache", overwrite: bool = False) -> str:
    """
    Internal helper to save a dictionary as a JSON file.

    Args:
        data (dict): Dictionary to save.
        filename, directory, overwrite: Filename, directory path, and overwrite preference.
    Returns:
        str: Path to the saved file.
    """
    filepath = _resolve_filepath(filename, directory, overwrite)
    pprint(filepath)
    _write_json_to_file(data, filepath)
    debug_print(f"Dictionary saved to: {filepath}")
    return filepath


def _save_list_of_dicts_to_json(data: list, filename: str = None, directory: str = "cache",
                                overwrite: bool = False) -> str:
    """
    Internal helper to save a list of dictionaries as a JSON file.
    """
    filepath = _resolve_filepath(filename, directory, overwrite)
    _write_json_to_file(data, filepath)
    debug_print(f"List of dictionaries saved to: {filepath}")
    return filepath

def _resolve_filepath(filename: str, directory: str, overwrite: bool) -> str:
    """
    Resolves the file path for saving, handling overwrites or generating unique names.

    Args:
        filename (str): Desired filename (with or without `.json` extension).
        directory (str): Path to the save directory, relative to repo root unless absolute.
        overwrite (bool): Allow overwriting existing files.

    Returns:
        str: Final resolved filepath.
    """
    repo_root = get_repo_root()  # Get the repository root directory

    # Ensure the directory is interpreted relative to the repo root unless it's absolute
    if not os.path.isabs(directory):
        directory = os.path.join(repo_root, directory)  # Resolve relative directory to repo root

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Ensure the filename has a `.json` extension
    base_filename = filename if filename else datetime.now().strftime("%m-%d-%H%M")
    if not base_filename.endswith(".json"):
        base_filename += ".json"

    filepath = os.path.join(directory, base_filename)

    # If overwriting is not allowed, handle unique filenames
    if not overwrite:
        for suffix in ascii_lowercase:
            if not os.path.exists(filepath):
                break
            filepath = os.path.join(directory, f"{base_filename[:-5]}-{suffix}.json")

    return filepath


def _write_json_to_file(data, filepath: str) -> None:
    """
    Helper to write JSON data to a file.

    Args:
        data: JSON serializable data.
        filepath (str): Filepath where to save the JSON.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    test_dict = {
        "name": "John Doe",
        "age": 30,
        "skills": ["Python", "Data Analysis"],
    }
    save_object_to_file(test_dict, filename="test_dict.json", directory="cache", overwrite=True)

    test_list = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 32},
    ]
    save_object_to_file(test_list, directory="cache")