import base64
import contextlib
import logging
import time
import threading
import pika
from huey.api import Huey
from huey.constants import EmptyData
from huey.storage import BaseStorage

# The pika logging is too verbose even on info.
logging.getLogger("pika").setLevel(logging.WARNING)

class AMQPStorage(BaseStorage):
    def __init__(self, name='huey', broker_url='amqp://guest:guest@localhost', consume=False, **storage_kwargs):
        super(AMQPStorage, self).__init__(name)
        self._broker_url = broker_url
        self._consume = consume
        self._task_queue_name = self.name
        self._schedule_queue_name = "%s.schedule"%self.name
        self._key_value_queue_name = "%s.key_value"%self.name
        self._queue = []
        self._schedule = []
        # Note that the fact that the inter thread channel sharing even works is a slight miracle.tt
        thread = threading.Thread(target=self._amqp_init)
        thread.daemon = True
        thread.start()
    
    def _amqp_init(self):        
        self.connection = pika.BlockingConnection(pika.URLParameters(self._broker_url))
        self.channel = self.connection.channel()
        self.initialize_queues()
        if self._consume:
            self.start_consuming()

    def initialize_queues(self):
        chan = self.channel
        chan.queue_declare(queue=self._task_queue_name, durable=True)
        chan.queue_declare(queue=self._schedule_queue_name, durable=True)
        chan.queue_declare(queue=self._key_value_queue_name, durable=True)
        chan.exchange_declare(exchange=self._schedule_queue_name, exchange_type="x-delayed-message", durable=True, arguments={"x-delayed-type": "fanout"})
        chan.queue_bind(exchange=self._schedule_queue_name, queue=self._schedule_queue_name)

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=10)
        self.channel.basic_consume(self._handle_queue, queue=self._task_queue_name)
        self.channel.basic_consume(self._handle_schedule, queue=self._schedule_queue_name)
        self.channel.start_consuming()
    
    def _handle_schedule(self, channel, method, props, body):
        self._schedule.append((method.delivery_tag, body))

    def _handle_queue(self, channel, method, props, body):
        self._queue.append((method.delivery_tag, body))

    @contextlib.contextmanager
    def _key_value_storage(self, republish=False):
        chan = self.channel
        resp, props, _ = chan.basic_get(queue=self._key_value_queue_name)
        if not resp:
            storage = {}
            republish = True
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
        else:
            if resp:
                chan.basic_reject(resp.delivery_tag)

    def enqueue(self, data):
        chan = self.channel
        chan.basic_publish(exchange="", routing_key=self._task_queue_name, body=data, properties=pika.BasicProperties(delivery_mode=2))

    def dequeue(self):
        try:
            tag, body = self._queue.pop(0)
        except IndexError:
            return None
        self.channel.basic_ack(tag)        
        return body
    
    def unqueue(self, data):
        # Somewhat expensive, because we must perform a linear search through the entire queue.
        indexes = []
        for tag, body in self._queue:
            if body == data:
                self.channel.basic_ack(tag)
        for idx in indexes:
            del self._queue[idx]
    
    def queue_size(self):
        return len(self._queue)
    
    def enqueued_items(self, limit=None):
        return [item[1] for item in self._queue[:limit]]
    
    def flush_queue(self):
        self.channel.queue_purge(self._task_queue_name)
        self._queue.clear()

    def add_to_schedule(self, data, ts):
        delay = ts.timestamp() - time.time()
        props = pika.BasicProperties()
        props.headers["x-delay"] = str(int(delay * 1000))
        props.delivery_mode = 2
        self.channel.basic_publish(exchange=self._schedule_queue_name, body=data, properties=props)

    def read_schedule(self, ts):
        # We currently assume that ts represents current time. No usage pattern in the huey consumer indicates it being anything else.
        items = self._schedule
        if not items:
            return []
        bodies = [item[1] for item in items]
        max_delivery_tag = max(items, key=lambda item: item[0])
        self.channel.basic_ack(max_delivery_tag, multiple=True)
        self._schedule.clear()
        return bodies
    
    def schedule_size(self):
        return len(self._schedule)

    def scheduled_items(self, limit=None):

        matching = self._all_messages_in_queue_matching(chan, self._schedule_queue_name, lambda resp, props, body: True, limit=limit)
        chan.close()
        return [item[2] for item in self._schedule[:limit]]
    
    def flush_schedule(self):
        self.channel.queue_purge(self._schedule_queue_name)
        self._schedule.clear()

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
    def get_storage(self, broker_url='amqp://guest:guest@localhost', consume=False, **kwargs):
        print(kwargs)
        return AMQPStorage(
            name=self.name,
            broker_url=broker_url,
            consume=consume,
            **kwargs)
