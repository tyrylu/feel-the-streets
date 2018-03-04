import os
from . import app

def get_huey_kwargs():
    return dict(broker_url=app.config["AMQP_BROKER_URL"], consume=os.environ.get("CONSUME", "False") == "True")