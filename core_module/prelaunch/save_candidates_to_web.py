import os
import json

from core_module.utils.util import debug_print
from core_module.utils.file_utils import get_repo_root


def save_candidates_to_json_file_in_web_root(candidates, filename="candidates.json"):
    """
    Saves the candidates dictionary to a JSON file located in the web/assets directory.

    :param candidates: List of candidates to save
    :param filename: Name of the JSON file (default is 'candidates.json')
    """
    # Base directory (project root)
    project_root = get_repo_root()  # Adjusts dynamically to the file's location
    # Directory to save the JSON file relative to the project root
    save_directory = os.path.join(project_root, "web","static", "assets")
    os.makedirs(save_directory, exist_ok=True)  # Creates the directory if it doesn't already exist

    # Full file path for the JSON file
    file_path = os.path.join(save_directory, filename)

    # Save the candidates data as a JSON file
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(candidates, json_file, indent=4, ensure_ascii=False)
        debug_print(f"Candidates successfully saved to {file_path}")
    except Exception as e:
        debug_print(f"Error saving candidates to JSON file: {e}")