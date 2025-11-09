import os
from .db.dao.candidates_dao import CandidatesDAO
from core_module.utils.file_utils import get_repo_root, save_object_to_file, load_json_file


class CardCacheService:
    """
    Manages a file-based cache for the results of the expensive
    find_profitable_candidates2 query.
    """
    CACHE_FILENAME = "profitable_candidates_cache.json"
    CACHE_DIR = "cache"

    def __init__(self, candidates_dao: CandidatesDAO):
        self.candidates_dao = candidates_dao
        self._cache_file_path = os.path.join(get_repo_root(), self.CACHE_DIR, self.CACHE_FILENAME)

    def get_cached_cards(self):
        """
        Loads profitable candidate cards from the file cache.
        If the cache is empty or doesn't exist, it populates it first.
        """
        if not os.path.exists(self._cache_file_path):
            print("Cache miss. Populating profitable candidates cache...")
            return self.refresh_cache()

        print("Cache hit. Loading profitable candidates from file.")
        # Assuming load_json_file returns the data directly
        return load_json_file(self._cache_file_path)

    def refresh_cache(self):
        """
        Forces a refresh of the cache by re-running the database query
        and saving the results to the cache file.
        """
        print("Refreshing profitable candidates cache from database...")
        # These parameters could be made configurable if needed in the future
        cards = self.candidates_dao.find_profitable_candidates2(
            min_value_increase=40,
            min_psa10_price=80,
            grading_cost=40,
            min_net_gain=0
        )
        save_object_to_file(cards, filename=self.CACHE_FILENAME, directory=self.CACHE_DIR, overwrite=True)
        print(f"Cache refreshed with {len(cards)} cards.")
        return cards

    def invalidate_cache(self):
        """
        Invalidates the cache by deleting the cache file.
        """
        if os.path.exists(self._cache_file_path):
            os.remove(self._cache_file_path)
            print("Profitable candidates cache has been invalidated.")
