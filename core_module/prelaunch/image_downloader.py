import os
import urllib

import requests

from core_module.utils.util import debug_print
from core_module.utils.file_utils import get_repo_root, load_json_file


def download_images_to_web_root(candidates):
    # Base directory (project root)
    project_root = get_repo_root()  # Adjusts dynamically to the file's location
    # Directory to save images relative to the project root
    save_directory = os.path.join(project_root, "web","backend", "static", "assets", "images")
    os.makedirs(save_directory, exist_ok=True)  # Creates the directory if it doesn't already exist
    # Download each image and save to the specified directory
    for card in candidates:
        url = card["card_data"]['img_url']
        decoded_url = urllib.parse.unquote(url)  # Decode URL to handle '%XX' encoded characters
        image_name = f"{decoded_url.split('/')[-2]}_{decoded_url.split('/')[-1]}"
        save_path = os.path.join(save_directory, image_name)
        # Calculate the relative path for web access
        relative_path_for_web = f"static/assets/images/{image_name}"
        # Check if the image already exists
        if os.path.exists(save_path):
            debug_print(f"File already exists: {save_path}, skipping download.")
        else:
            debug_print(f"Downloading {url}...")
            try:
                response = requests.get(url, timeout=10)  # Add timeout for safety
                if response.status_code == 200:
                    # Save the content to the target file path
                    with open(save_path, "wb") as file:
                        file.write(response.content)
                    debug_print(f"Saved: {save_path}")
                else:
                    debug_print(f"Failed to download: {url} (Status code: {response.status_code})")
                    continue
            except Exception as e:
                debug_print(f"Error downloading {url}: {e}")
                continue
        # Add the relative path to the card dictionary
        card["local_image"] = image_name
        debug_print(f"Updated candidate with local image path: {relative_path_for_web}")
    return candidates

if __name__ == '__main__':
    candidates = load_json_file("cache/candidates.json")
    download_images_to_web_root(candidates)