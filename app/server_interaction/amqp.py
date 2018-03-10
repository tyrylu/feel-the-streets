import pickle
from collections import defaultdict
import pika
from ..services import config
from shared.amqp_queue_naming import get_client_queue_name


class SemanticChangeRetriever:

    def __init__(self):
        self._conn = pika.BlockingConnection(pika.URLParameters(config().amqp_broker_url))
        self._chan = self._conn.channel()
        self._max_delivery_tags = defaultdict(lambda: 0)

    def new_changes_in(self, area):
        queue_name = get_client_queue_name(config().client_id, area)
        while True:
            method, props, body = self._chan.basic_get(queue_name)
            if not method:
                break
            self._max_delivery_tags[area] = method.delivery_tag
            yield pickle.loads(body)

    def acknowledge_changes_for(self, area):
        if area not in self._max_delivery_tags:
            raise ValueError("Changes for area %s not requested yet."%area)
        self._chan.basic_ack(self._max_delivery_tags[area], multiple=True)
    
    def __del__(self):
        self._chan.close()
        self._conn.close()


    def new_change_count_in(self, area):
        resp = self._chan.queue_declare(get_client_queue_name(config().client_id, area), passive=True, durable=True)
        return resp.method.message_count