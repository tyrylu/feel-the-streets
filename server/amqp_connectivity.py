import contextlib
import pika
from . import app

@contextlib.contextmanager
def administrative_channel():
    with pika.BlockingConnection(pika.URLParameters(app.config["AMQP_BROKER_URL"])) as conn:
        chan = conn.channel()
        yield chan
        chan.close()