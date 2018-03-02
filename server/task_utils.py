import logging
from . import huey
from .huey_creation import get_huey_kwargs
from . import app

log = logging.getLogger(__name__)

def enqueue_with_retries(task, attempt=1, *args, **kwargs):
    if attempt > app.config["ENQUEUE_RETRIES"]:
        log.error("Max enqueue retry limit reached for task %s, giving up, task not enqueued!", task)
        return
    try:
        task(*args, **kwargs)
    except Exception:
        log.warn("Enqueue for task %s failed, reconnecting and retriing.")
        huey.storage = huey.get_storage(get_huey_kwargs())
        enqueue_with_retries(task, attempt=attempt + 1, *args, **kwargs)
