import sys, logging
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)
from server import app as application