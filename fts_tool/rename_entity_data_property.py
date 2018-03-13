import os
import json
import click
import pika
import dotenv
from . import cli
from shared.semantic_change import Change, ChangeType
from shared.diff_utils import DiffChange
from shared import Database
from shared.models import Entity

@cli.command()
@click.option("-o", "--old", help="The old field name", prompt=True)
@click.option("-n", "--new", help="The new name of the old field", prompt=True)
def rename_entity_data_property(old, new):
    dotenv.load_dotenv("server/.env")
    conn = pika.BlockingConnection(pika.URLParameters(os.environ["AMQP_BROKER_URL"]))
    chan = conn.channel()
    for info in Database.get_local_databases_info():
        print("Processing database %s."%name)
        db = Database(info["name"])
        for entity in db.query(Entity):
            data = json.loads(entity.data)
            if old in data:
                val = data[old]
                del data[old]
                data[new] = val
                entity.data = json.dumps(data)
                change = Change()
                change.osm_id = data["osm_id"]
                change.data_changes.append(DictChange.removing(old))
                change.data_changes.append(DictChange.creating(new, val))
                chan.basic_publish(info["name"], body=pickle.dumps(change, protocol=pickle.HIGHEST_PROTOCOL), properties=pika.BasicProperties(delivery_mode=2))
        db.commit()
    chan.close()
    conn.close()
    print("Success.")

