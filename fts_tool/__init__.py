import sys
import os
import click
import logging
from .log_aggregation import AggregatingFileHandler

def _configure_logging(suffix):
    os.makedirs("logs", exist_ok=True)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, handlers=[AggregatingFileHandler(os.path.join("logs", "db_generation_%s.log"%suffix), "w", "UTF-8"), sh])

@click.group()
def cli():
    pass

# Import them there, so the enironment exists
from . import database_updater
from . import model_enhancement_helper