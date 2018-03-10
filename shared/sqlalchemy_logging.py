from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logger = logging.getLogger(__name__)

total_spend = 0
last_finish = 0
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, 
                        parameters, context, executemany):
    now = time.time()
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, 
                        parameters, context, executemany):
    global total_spend, last_finish
    last_finish = time.time()
    total = time.time() - context._query_start_time
    if total < 1.0:
        return
    total_spend += total
    # Modification for StackOverflow: times in milliseconds
    logger.debug("Finished executing query:\n%s\nParameters: %s\nTotal Time: %.02fms\nCumulative time: %.02fms" % (statement, parameters, total*1000, total_spend*1000))