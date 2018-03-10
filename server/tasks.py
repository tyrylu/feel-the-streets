import pika
import logging
import pickle
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
    with administrative_channel() as chan:
        chan.exchange_declare(area_name, exchange_type="fanout", durable=True)
    log.info("Generation sequence complete.")

def update_area_databases_task(date=None):
    _configure_logging("update")
    for area in Area.query.all(): #filter_by(state=AreaState.updated):
        log.info("Processing area %s.", area.name)
        area.state = AreaState.getting_changes
        db.session.commit()
        processor = ChangeActionProcessor(area.name)
        first = True
        for change in processor.new_semantic_changes(date=date):
            if first:
                area.state = AreaState.applying_changes
                db.session.commit()
                first = False
            processor._db.apply_change(change)
            msg_bin = pickle.dumps(change, protocol=pickle.HIGHEST_PROTOCOL)
            huey.storage.channel.basic_publish(area.name, body=msg_bin, properties=pika.BasicProperties(delivery_mode=2), routing_key="")
        processor._db.commit()
        area.state = AreaState.updated
        db.session.commit()
        log.info("Geometry difference checks required retrieving %s objects.", processor._translator.manager.cached_total)
        processor._translator.manager.remove_temp_data()
        log.info("Finished processing area %s.", area.name)
        

