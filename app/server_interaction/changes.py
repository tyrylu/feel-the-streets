from osm_db import SemanticChange
from collections import defaultdict
import redis
from ..services import config

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
            raise ConnectionError() from e
        self._message_ids = defaultdict(list)

    def new_changes_in(self, area):
        messages = self._conn.xreadgroup(config().general.client_id, "fts_app", {f"fts.{area}.changes": "$"})
        for (message_id, data) in messages[0]:
            self._message_ids[area].append(message_id)
            yield SemanticChange.from_serialized(data)

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
        if not num:
            return 0
        return int(num)
    def redownload_requested_for(self, area):
        return bool(self._conn.sismember(f"fts.{area}.redownload_requests", config().general.client_id))