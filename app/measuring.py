import logging
import contextlib
import time

log = logging.getLogger(__name__)
@contextlib.contextmanager
def measure(label):
    start = time.time()
    yield
    log.debug("%s took %.2f ms", label, (time.time() - start) * 1000)