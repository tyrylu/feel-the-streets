import sys
import os
import logging
from .database_updater import DatabaseUpdater
from .change_action_processor import ChangeActionProcessor
from .log_aggregation import AggregatingFileHandler

def create_database(location, use_cache=False, save_responses=False):
    _configure_logging(location)
    updater = DatabaseUpdater(location=location, use_cache=use_cache, cache_responses=save_responses)
    updater.create_database(True)

    
def changes(location, date):
    _configure_logging(location)
    processor = ChangeActionProcessor(location)
    


import click


def _configure_logging(suffix):
    import shared.sqlalchemy_logging
    os.makedirs("logs", exist_ok=True)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, handlers=[AggregatingFileHandler(os.path.join("logs", "db_generation_%s.log"%suffix), "w", "UTF-8"), sh])
    logging.getLogger("shapely.geos").setLevel(logging.WARN)
