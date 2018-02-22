import click
from .. import _configure_logging, cli
from .database_updater import DatabaseUpdater
from .change_action_processor import ChangeActionProcessor

@cli.command()
@click.option("-l", "--location", prompt=True, help="The location for which to update the database")
@click.option("-u", "--use-cache", default=False, help="Whether to use the previously cached responses, if possible", is_flag=True)
@click.option("-s", "--save-responses", default=False, help="Whether to cache the responses from the OSM api", is_flag=True)
@click.option("-c", "--check-geometries", default=False, help="Whether to loading of the geometries using shapely should be attempted", is_flag=True)
def update_database(location, use_cache, save_responses, check_geometries):
    _configure_logging(location)
    updater = DatabaseUpdater(location, check_geometries, use_cache, save_responses)
    updater.update_database(True)
    input("Database update successful, press enter to exit.")
    
@cli.command()    
@click.option("-l", "--location", prompt=True, help="The location for which to update the database")
@click.option("-u", "--use-cache", default=False, help="Whether to use the previously cached responses, if possible", is_flag=True)
@click.option("-s", "--save-responses", default=False, help="Whether to cache the responses from the OSM api", is_flag=True)
@click.option("-c", "--check-geometries", default=False, help="Whether to loading of the geometries using shapely should be attempted", is_flag=True)
def interpret(location, use_cache, save_responses, check_geometries):
    _configure_logging(location)
    updater = DatabaseUpdater(location, check_geometries, use_cache, save_responses)
    for entity in updater.entities_in_location():
        pass
    input("Entity interpretation sequence successful.")

@cli.command()
@click.option("-l", "--location", help="The location for change retrieval", prompt=True)
@click.option("-d", "--date", help="Date to start the change sequence generation from, overrides the last date in the database", default=None)
def changes(location, date):
    _configure_logging(location)
    processor = ChangeActionProcessor(location)
    for action in processor.new_semantic_changes(date):
        print(action)
