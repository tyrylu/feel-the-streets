from osm_db import SemanticChange
from collections import defaultdict
import logging
import redis
from ..services import config

log = logging.getLogger(__name__)

class ConnectionError(RuntimeError):
    pass

class SemanticChangeRetriever:

    def __init__(self):
        self._needs_closing = False
        self._needs_channel_closing = False
        try:
            self._conn = redis.Redis.from_url(config().redis_url)
            self._conn.ping()
            self._needs_closing = True
        except redis.RedisError as e:
            log.warning("Failed to connect to redis: %s", e)
            raise ConnectionError() from e
        self._message_ids = defaultdict(list)

    def new_changes_in(self, area):
        reply = self._conn.xreadgroup(config().general.client_id, "fts_app", {f"fts.{area}.changes": ">"})
        messages = reply[0][1]
        for (message_id, data) in messages:
            self._message_ids[area].append(message_id)
            yield SemanticChange.from_serialized(data[b"c"])

    def acknowledge_changes_for(self, area):
        if area not in self._message_ids:
            raise ValueError("Changes for area %s not requested yet."%area)
        self._conn.xack(f"fts.{area}.changes", config().general.client_id, *self._message_ids[area])
        self._conn.hincrby(f"fts.{area}.change_counts", config().general.client_id, -len(self._message_ids[area]))
    
    def close(self):
        if self._needs_closing:
            self._conn.close()
            self._needs_closing = False
            
    def __del__(self):
        self.close()
    
    def new_change_count_in(self, area):
        num = self._conn.hget(f"fts.{area}.change_counts", config().general.client_id)
        if num is None:
            return 0
        return int(num)
    
    def redownload_requested_for(self, area):
        try:
            changes_stream_exists = bool(self._conn.exists(f"fts.{area}.changes"))
        except redis.exceptions.NoPermissionError as e:
            print("Permission error", e)
            return True # We do not have the server side permissions yet, but we have a local copy, e. g. we are migrating from the old storage mechanism
        redownload_request_exists = bool(self._conn.sismember(f"fts.{area}.redownload_requests", config().general.client_id))
        return (not changes_stream_exists) or redownload_request_exists