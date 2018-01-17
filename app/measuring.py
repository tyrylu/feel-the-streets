import contextlib
import time

@contextlib.contextmanager
def measure(label):
    start = time.time()
    yield
    print("%s took %.2f ms"%(label, (time.time() - start) * 1000))