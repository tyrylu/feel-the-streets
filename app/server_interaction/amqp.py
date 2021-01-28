from osm_db import SemanticChange
from collections import defaultdict
import pika
from ..services import config
from ..amqp_queue_naming import get_client_queue_name

class ConnectionError(RuntimeError):
    pass

class UnknownQueueError(RuntimeError):
    pass

class SemanticChangeRetriever:

    def __init__(self):
        self._needs_closing = False
        self._needs_channel_closing = False
        try:
            self._conn = pika.BlockingConnection(pika.URLParameters(config().amqp_broker_url))
            self._chan = self._conn.channel()
            self._needs_closing = True
            self._needs_channel_closing = True
        except Exception as e:
            raise ConnectionError() from e
        self._max_delivery_tags = defaultdict(lambda: 0)

    def new_changes_in(self, area):
        queue_name = get_client_queue_name(config().general.client_id, area)
        while True:
            method, props, body = self._chan.basic_get(queue_name)
            if not method:
                break
            self._max_delivery_tags[area] = method.delivery_tag
            yield SemanticChange.from_serialized(body)

    def acknowledge_changes_for(self, area):
        if area not in self._max_delivery_tags:
            raise ValueError("Changes for area %s not requested yet."%area)
        self._chan.basic_ack(self._max_delivery_tags[area], multiple=True)
    
    def close(self):
        if self._needs_channel_closing:
            self._chan.close()
            self._needs_channel_closing = False
        if self._needs_closing:
            self._conn.close()
            self._needs_closing = False
            
    def __del__(self):
        self.close()
    
    def new_change_count_in(self, area):
        try:
            resp = self._chan.queue_declare(get_client_queue_name(config().general.client_id, area), passive=True, durable=True)
        except Exception as e:
            self._needs_channel_closing = False
            raise UnknownQueueError() from e
        return resp.method.message_count