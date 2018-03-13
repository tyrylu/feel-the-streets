import click
@click.group()
def cli():
    pass

# Import them there, so the environment exists

from . import model_enhancement_helper
from . import rename_entity_data_property