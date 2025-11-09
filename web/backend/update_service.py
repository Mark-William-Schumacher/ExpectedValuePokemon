import os
import sys

# This adds the project root to the Python path to allow for absolute imports.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from web.backend.card_cache_service import CardCacheService
from web.backend.db.dao.candidates_dao import CandidatesDAO
from web.backend.db.dao.gem_rate_refresh_log_dao import GemRateRefreshLogDAO
from web.backend.db.dao.psa_dao import PsaDAO
from web.backend.db.dao.sales_dao import SalesDAO
from web.backend.db.dao.sales_volume_refresh_log_dao import SalesVolumeRefreshLogDAO
from web.backend.db.dao.set_dao import SetDAO
from web.backend.db.util.cache_to_db_migation import populate_card_analytics_from_db, populate_grading_financials_from_db
from core_module.service.domain import get_volume_of_transactions, get_card_id_psa_pop, get_card_prices


class UpdateService:
    """
    A service class to handle the logic for updating and maintaining card data.
    """

    def __init__(
            self,
            candidates_dao: CandidatesDAO,
            psa_dao: PsaDAO,
            sales_dao: SalesDAO,
            set_dao: SetDAO,
            sales_volume_refresh_log_dao: SalesVolumeRefreshLogDAO,
            gem_rate_refresh_log_dao: GemRateRefreshLogDAO,
            card_cache_service: CardCacheService
    ):
        """
        Initializes the service with all its dependencies.
        """
        self.candidates_dao = candidates_dao
        self.psa_dao = psa_dao
        self.sales_dao = sales_dao
        self.set_dao = set_dao
        self.sales_volume_refresh_log_dao = sales_volume_refresh_log_dao
        self.gem_rate_refresh_log_dao = gem_rate_refresh_log_dao
        self.card_cache_service = card_cache_service

    def _update_sales_price_data(self, set_ids):
        """
        Private method to fetch and update card prices for a list of sets.
        """
        if not set_ids:
            return
        for set_id in set_ids:
            print(f"Updating sales price data for set_id: {set_id}")
            data = get_card_prices(set_id, use_network_only=True)
            self.set_dao.add_set_from_json(data)

    def _update_missing_sales_volume_cards(self, card_ids):
        """
        Private method to fetch and update sales volume for a list of cards
        and log the refresh attempt.
        """
        if not card_ids:
            return

        for card_id in card_ids:
            print(f"Trying to update sales volume for card_id: {card_id}")
            data = get_volume_of_transactions(card_id, use_network_only=True)
            self.sales_dao.add_sales_from_json(data)
            self.sales_volume_refresh_log_dao.log_batch_refresh_attempt([card_id])


    def _update_missing_psa_pops(self, card_ids):
        """
        Private method to fetch and update PSA population data for a list of cards
        and log the refresh attempt.
        """
        if not card_ids:
            return

        for card_id in card_ids:
            print(f"Trying to update PSA pop for card_id: {card_id}")
            data = get_card_id_psa_pop(card_id, use_network_only=True)
            if data and isinstance(data, dict) and len(data) > 2:
                try:
                    self.psa_dao.add_psa_population_from_json(card_id, data)
                except Exception as e:
                    print(e)
            self.gem_rate_refresh_log_dao.log_batch_refresh_attempt([card_id])

    def run_update_cycle(self):
        """
        Runs the full update cycle for fetching missing data, processing it,
        and invalidating the cache.
        """
        print("--- Starting update cycle ---")

        # 1. Update stale set data
        print("\nChecking for stale set data...")
        stale_sets_from_db = self.set_dao.get_stale_outdated_sets_list(1)
        if stale_sets_from_db:
            print(f"Found {len(stale_sets_from_db)} stale sets to update: {stale_sets_from_db}")
            self._update_sales_price_data(stale_sets_from_db)
        else:
            print("No stale set data to update.")

        # 2. Find and update cards missing PSA population data
        print("\nFinding profitable candidates without recent gem rate data...")
        card_ids_without_gem_rate = self.candidates_dao.get_card_id_list_of_profitable_cards_without_gem_rate(
            min_value_increase=50, min_psa10_price=80)

        if card_ids_without_gem_rate:
            print(f"Found {len(card_ids_without_gem_rate)} cards to update PSA pop data for.")
            self._update_missing_psa_pops(card_ids_without_gem_rate)
        else:
            print("No cards need PSA pop updates at this time.")

        # 3. Find and update cards missing sales volume
        print("\nFinding profitable candidates without recent sales volume...")
        list_of_volume_data_cards = self.candidates_dao.find_profitable_candidates_without_sales_volume(20, 70,
                                                                                                         days_since_last_attempt=7)
        card_ids_without_volume = [candidate['card_id'] for candidate in list_of_volume_data_cards]

        if card_ids_without_volume:
            print(f"Found {len(card_ids_without_volume)} cards to update sales volume for.")
            self._update_missing_sales_volume_cards(card_ids_without_volume)
        else:
            print("No cards need sales volume updates at this time.")

        # 4. Populate analytics and financials for all cards
        print("\nPopulating card analytics for all cards...")
        populate_card_analytics_from_db(self.psa_dao)


        print("\nPopulating grading financials for all cards...")
        populate_grading_financials_from_db(self.candidates_dao)

        # 5. Invalidate the cache to force a refresh on the next API call
        print("\nInvalidating card cache...")
        self.card_cache_service.invalidate_cache()

        print("\n--- Update cycle finished ---")


if __name__ == '__main__':
    from web.backend.containers import AppContainer

    # Setup the dependency injection container
    app_container = AppContainer()
    app_container.wire(modules=[__name__])

    # Get an instance of the UpdateService from the container
    update_service_instance = app_container.update_service()

    # Execute the update cycle
    update_service_instance.run_update_cycle()