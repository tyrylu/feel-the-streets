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
    logger.debug("Start Query:\n%s\nFrom last query finish: %.2fms" % (statement, (now - last_finish) * 1000))
    # Modification for StackOverflow answer:
    # Show parameters, which might be too verbose, depending on usage..
    logger.debug("Parameters:\n%r" % (parameters,))


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, 
                        parameters, context, executemany):
    global total_spend, last_finish
    last_finish = time.time()
    total = time.time() - context._query_start_time
    total_spend += total
    # Modification for StackOverflow: times in milliseconds
    logger.debug("Query finished!\nTotal Time: %.02fms\nCumulative time: %.02fms" % (total*1000, total_spend*1000))