
@click.group()
def cli():
    pass

# Import them there, so the enironment exists
from . import database_updater
from . import model_enhancement_helper