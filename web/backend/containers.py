from . import config  # Import the new config module
from dependency_injector import containers
from dependency_injector.providers import Configuration, Factory, Resource, Singleton

from .card_cache_service import CardCacheService
from .db.dao.candidates_dao import CandidatesDAO
from .db.dao.gem_rate_refresh_log_dao import GemRateRefreshLogDAO
from .db.dao.psa_dao import PsaDAO
from .db.dao.sales_volume_refresh_log_dao import SalesVolumeRefreshLogDAO
from .db.dao.set_dao import SetDAO
from .db.database import Database
from .db.dao.sales_dao import SalesDAO
from .update_service import UpdateService


class AppContainer(containers.DeclarativeContainer):
    """
    The central DI container for the application.

    This class declares all the application's services and their dependencies.
    It's the equivalent of a Dagger/Hilt Module.
    """

    # --- Configuration Section ---
    # You can load configs from files, env vars, etc.
    # The configuration is now initialized with a default value for the database path
    # taken from our central config module.
    config = Configuration(
        default={
            "db": {
                "path": config.DEFAULT_DB_PATH
            }
        }
    )

    # --- Service Providers Section ---

    database = Resource(
            Database,
            db_path=config.db.path,
        )

    # SalesDAO provider: Defined as a Factory.
    # Every time we request a 'sales_dao', it will create a new instance.
    # This is our @Provides.
    sales_dao = Factory(
        SalesDAO,
        conn=database.provided.conn  # Dependency is injected here!
    )

    # Add the SetDAO provider, which also depends on the database connection.
    set_dao = Factory(
        SetDAO,
        conn=database.provided.conn,
        candidates_dao=Factory(lambda: AppContainer.candidates_dao())
    )

    # Add the SetDAO provider, which also depends on the database connection.
    psa_dao = Factory(
        PsaDAO,
        conn=database.provided.conn,
        candidates_dao=Factory(lambda: AppContainer.candidates_dao())
    )

    candidates_dao = Factory(
        CandidatesDAO,
        conn=database.provided.conn
    )

    sales_volume_refresh_log_dao = Factory(
        SalesVolumeRefreshLogDAO,
        conn=database.provided.conn
    )

    card_cache_service = Singleton(
        CardCacheService,
        candidates_dao=candidates_dao
    )

    gem_rate_refresh_log_dao = Factory(
        GemRateRefreshLogDAO,
        conn=database.provided.conn
    )

    update_service = Factory(
        UpdateService,
        candidates_dao=candidates_dao,
        psa_dao=psa_dao,
        sales_dao=sales_dao,
        set_dao=set_dao,
        sales_volume_refresh_log_dao=sales_volume_refresh_log_dao,
        gem_rate_refresh_log_dao=gem_rate_refresh_log_dao,
        card_cache_service=card_cache_service,
    )




