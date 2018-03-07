import logging
from . import db, huey
from .models import Area, AreaState
from .area_database_updater import create_database, _configure_logging
from .area_database_updater.change_action_processor import ChangeActionProcessor
from shared import Database

log = logging.getLogger(__name__)
@huey.task()
def create_database_task(area_name):
    create_database(area_name)
    area = Area.query.filter_by(name=area_name).first()
    area.state = AreaState.updated
    db.session.commit()
    log.info("Generation sequence complete.")

def update_area_databases_task():
    _configure_logging("update")
    for area in Area.query.all(): #filter_by(state=AreaState.updated):
        log.info("Processing area %s.", area.name)
        area.state = AreaState.getting_changes
        db.session.commit()
        processor = ChangeActionProcessor(area.name)
        first = True
        for change in processor.new_semantic_changes("2018-03-07T00:00:00"):
            if first:
                area.state = AreaState.applying_changes
                db.session.commit()
                first = False
            processor._db.apply_change(change)
        processor._db.commit()
        area.state = AreaState.updated
        db.session.commit()
        processor._translator.manager.remove_temp_data()
        log.info("Finished processing area %s.", area.name)

