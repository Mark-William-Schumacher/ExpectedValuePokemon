import os

"""
A central configuration module for the application.

This file acts as the single source of truth for project-wide constants,
especially file system paths. By calculating paths based on this file's location,
we ensure they are always correct regardless of where the application's scripts are run from.
"""

# Define the absolute path to the project root directory.
# `__file__` is the path to this config.py file. We navigate up two levels to get to the root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# --- Database Configuration ---
# Define the default path for the SQLite database, relative to the project root.
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "web/backend/pokemon.db")

# You can add other paths here later, for example:
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache/api_responses")
