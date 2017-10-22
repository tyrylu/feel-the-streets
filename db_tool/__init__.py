import sys
import logging
from .log_aggregation import AggregatingFileHandler
from .database_updater import DatabaseUpdater


log = logging.getLogger(__name__)

def _configure_logging(suffix):
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG, handlers=[AggregatingFileHandler("db_generation_%s.log"%suffix, "w", "UTF-8"), sh])

def update_database():
    location = input("Location name: ")
    _configure_logging(location)
    updater = DatabaseUpdater(location)
    updater.update_database()
    updater.translator.record.save_to_file("generation_record_%s.txt"%location)
    input("Database update successful, press enter to exit.")