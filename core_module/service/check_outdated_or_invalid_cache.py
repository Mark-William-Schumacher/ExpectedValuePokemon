import sys
import os
import json
from datetime import datetime, timedelta

from core_module.utils.file_utils import get_api_response_cache_dir


def get_outdated_or_invalid_files_with_diagnostics():
    """
    Check JSON files and identify outdated files, null data, or encoding issues.

    Returns:
    - A list of invalid files.
    """
    # Simulate the cache_dir function
    cache_dir = get_api_response_cache_dir()
    invalid_files = []
    time_threshold = datetime.now() - timedelta(hours=48)

    # Get all JSON files in the directory
    all_files = [file_name for file_name in os.listdir(cache_dir) if file_name.endswith('.json')]
    total_files = len(all_files)

    # Iterate files, tracking progress
    for i, file_name in enumerate(all_files, start=1):
        file_path = os.path.join(cache_dir, file_name)
        try:
            # Check JSON validity
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if `updated_date` exists and is older than 48 hours
            if 'updated_date' in data:
                try:
                    updated_date = datetime.strptime(data['updated_date'], "%Y-%m-%d %H:%M:%S")
                    if updated_date < time_threshold:  # If it's outdated
                        invalid_files.append(file_path)
                        continue
                except ValueError:
                    invalid_files.append(file_path)
                    continue
            else:
                invalid_files.append(file_path)
                continue

            # Check if `data` exists and is null
            if 'data' not in data or data['data'] is None:
                other_keys = [key for key in data.keys() if key != 'updated_date']
                if len(other_keys) == 0:
                    invalid_files.append(file_path)
                    continue
        except Exception:
            invalid_files.append(file_path)

        # Update progress on the same console line
        # Use \r to return the cursor to the start of the line and overwrite
        sys.stdout.write(f"\rProcessing files... {i}/{total_files} files checked.")
        sys.stdout.flush()

    # Finalize with a new line after progress ends
    print("\nProcessing complete!")

    # Return the list of invalid files
    return invalid_files

def find_problematic_line(file_path):
    """
    Identify the exact line in a file that causes a Unicode decoding issue.

    Args:
    - file_path (str): The path to the file to analyze.

    Returns:
    - None: Prints out the lines and character positions causing decoding issues.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                try:
                    # Try encoding and decoding the line to pinpoint issues
                    line.encode('utf-8').decode('utf-8')
                except UnicodeDecodeError as e:
                    print(f"Decoding error in file '{file_path}' at line {line_no}:")
                    print(f"  Problematic part: {line[e.start:e.end]} (Position {e.start}-{e.end})")
                    break
    except Exception as e:
        print(f"An error occurred while reading the file '{file_path}': {e}")


# Call the function
get_outdated_or_invalid_files_with_diagnostics()