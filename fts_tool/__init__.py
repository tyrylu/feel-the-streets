import sys
import click
import logging
from .log_aggregation import AggregatingFileHandler

def _configure_logging(suffix):
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[AggregatingFileHandler("db_generation_%s.log"%suffix, "w", "UTF-8"), sh])

@click.group()
def cli():
    pass

# Import them there, so the enironment exists
from . import database_updater