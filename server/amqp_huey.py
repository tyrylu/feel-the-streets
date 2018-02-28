import base64
import contextlib
import logging
import time
import pika
from huey.api import Huey
from huey.constants import EmptyData
from huey.storage import BaseStorage

# The pika logging is too verbose even on info.
logging.getLogger("pika").setLevel(logging.WARNING)

class AMQPStorage(BaseStorage):
    def __init__(self, name='huey', broker_url='amqp://guest:guest@localhost', **storage_kwargs):
        super(AMQPStorage, self).__init__(name)
        self._task_queue_name = self.name
        self._schedule_queue_name = "%s.schedule"%self.name
        self._key_value_queue_name = "%s.key_value"%self.name
        self.connection = pika.BlockingConnection(pika.URLParameters(broker_url))
        self.initialize_queues()

    def initialize_queues(self):
        chan = self.connection.channel()
        chan.queue_declare(queue=self._task_queue_name, durable=True)
        chan.queue_declare(queue=self._schedule_queue_name, durable=True)
        chan.queue_declare(queue=self._key_value_queue_name, durable=True)
        chan.exchange_declare(exchange=self._schedule_queue_name, exchange_type="x-delayed-message", durable=True, arguments={"x-delayed-type": "fanout"})
        chan.queue_bind(exchange=self._schedule_queue_name, queue=self._schedule_queue_name)
        chan.close()
    
    def _all_messages_in_queue_matching(self, channel, queue_name, predicate=None, limit=None):
        matching = []
        resp, props, body = channel.basic_get(queue=queue_name)
        nth = 1
        while resp:
            if predicate and predicate(resp, props, body):
                predicate_match = True
            elif not predicate:
                predicate_match = True
            else:
                predicate_match = False
            if predicate_match and (limit is not None and nth <= limit):
                matching.append((resp, props, body))
                nth += 1
            resp, props, body = channel.basic_get(queue=queue_name)
        return matching
    
    def _queue_size(self, queue):
        chan = self.connection.channel()
        resp = chan.queue_declare(queue=queue, passive=True)
        chan.close()
        return resp.method.message_count

    @contextlib.contextmanager
    def _key_value_storage(self, republish=False):
        chan = self.connection.channel()
        resp, props, _ = chan.basic_get(queue=self._key_value_queue_name)
        if not resp:
            storage = {}
        else:
            storage = props.headers or {}
        yield storage
        if republish:
            if resp:
                chan.basic_ack(resp.delivery_tag)
            props = pika.BasicProperties()
            props.headers = storage
            props.delivery_mode = 2
            chan.basic_publish(exchange="", routing_key=self._key_value_queue_name, body="See the headers.", properties=props)

    def enqueue(self, data):
        chan = self.connection.channel()
        chan.basic_publish(exchange="", routing_key=self._task_queue_name, body=data, properties=pika.BasicProperties(delivery_mode=2))
        chan.close()

    def dequeue(self):
        chan = self.connection.channel()
        resp, props, body = chan.basic_get(queue=self._task_queue_name, no_ack=True)
        chan.close()
        return body
    
    def unqueue(self, data):
        # Somewhat expensive, because we must perform a linear search through the entire queue.
        chan = self.connection.channel()
        matching = self._all_messages_in_queue_matching(chan, self._task_queue_name, lambda resp, props, body: body == data)
        for resp, _, _ in matching:
            chan.basic_ack(resp.delivery_tag)
        chan.close()
    
    def queue_size(self):
        return self._queue_size(self._task_queue_name)
    
    def enqueued_items(self, limit=None):
        chan = self.connection.channel()
        matching = self._all_messages_in_queue_matching(chan, self._task_queue_name, lambda resp, props, body: True, limit=limit)
        chan.close()
        return [item[2] for item in matching]
    
    def flush_queue(self):
        chan = self.connection.channel()
        chan.queue_purge(self._task_queue_name)
        chan.close()

    def add_to_schedule(self, data, ts):
        delay = ts.timestamp() - time.time()
        props = pika.BasicProperties()
        props.headers["x-delay"] = str(int(delay * 1000))
        props.delivery_mode = 2
        chan = self.connection.channel()
        chan.basic_publish(exchange=self._schedule_queue_name, body=data, properties=props)
        chan.close()

    def read_schedule(self, ts):
        # We currently assume that ts represents current time. No usage pattern in the huey consumer indicates it being anything else.
        chan = self.connection.channel()
        items = self._all_messages_in_queue_matching(chan, self._schedule_queue_name, lambda resp, props, body: True)
        if not items:
            return []
        bodies = [item[2] for item in items]
        max_delivery_tag = max(items, key=lambda item: item[0].delivery_tag)
        chan.basic_ack(max_delivery_tag, multiple=True)
        chan.close()
        return bodies
    
    def schedule_size(self):
        return self._queue_size(self._schedule_queue_name)

    def scheduled_items(self, limit=None):
        chan = self.connection.channel()
        matching = self._all_messages_in_queue_matching(chan, self._schedule_queue_name, lambda resp, props, body: True, limit=limit)
        chan.close()
        return [item[2] for item in matching]
    
    def flush_schedule(self):
        chan = self.connection.channel()
        ch.queue_purge(self._schedule_queue_name)
        chan.close()

    def put_data(self, key, value):
        value = base64.b64encode(value).decode("ascii")
        with self._key_value_storage(republish=True) as storage:
            storage[key] = value

    def peek_data(self, key):
        with self._key_value_storage(republish=False) as storage:
            data = storage.get(key, None)
            if data:
                return base64.b64decode(data)
            else:
                return EmptyData
    
    def pop_data(self, key):
        with self._key_value_storage(republish=True) as storage:
            val = storage.pop(key, None)
            if val:
                return base64.b64decode(val)
            else:
                return EmptyData
    
    def has_data_for_key(self, key):
        with self._key_value_storage(republish=False) as storage:
            return key in storage

    def result_store_size(self):
        with self._key_value_storage(republish=False) as storage:
            return len(storage)

    def flush_results(self):
        chan = self.connection.channel()
        chan.queue_purge(self._key_value_queue_name)

    def put_error(self, metadata):
        pass

    def get_error(self, limit=None, offset=0):
        pass

    def flush_errors(self):
        pass

    def emit(self, message):
        pass

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration
    __next__ = next


class AMQPHuey(Huey):
    def get_storage(self, broker_url='amqp://guest:guest@localhost', **kwargs):
        return AMQPStorage(
            name=self.name,
            broker_url=broker_url,
            **kwargs)
