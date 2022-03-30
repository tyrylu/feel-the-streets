import sqlite3
from .models import LastLocation, Bookmark

# Yes, the area columns could be integers, but only if we wouldn't mess the schema when migrating to area ids in the past (maybe before 1.0?).
MAYBE_CREATE_MIGRATIONS = "CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY, version INTEGER NOT NULL, applied_at TEXT NOT NULL)"
MAYBE_CREATE_BOOKMARKS = "CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, area TEXT NOT NULL, name TEXT NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL, direction FLOAT NOT NULL DEFAULT 0.0);"
ADD_DIRECTION_TO_BOOKMARKS = "ALTER TABLE bookmarks ADD COLUMN direction FLOAT NOT NULL DEFAULT 0.0;"
LAST_LOCATION_NAME = ".lastloc"
DB_VERSION = 1

class AppDb:
    def __init__(self, db_path):
        self._db = sqlite3.connect(db_path)
        self._db.execute(MAYBE_CREATE_MIGRATIONS)
        self._migrate()
        res = self._db.execute("SELECT area, id from bookmarks where name = ?", (LAST_LOCATION_NAME,))
        self._last_location_ids = dict(res.fetchall())

    def add_bookmark(self, mark):
        self._db.execute("INSERT INTO bookmarks (name, area, latitude, longitude, direction) VALUES (?, ?, ?, ?, ?)", (mark.name, mark.area, mark.latitude, mark.longitude, mark.direction))
        self._db.commit()

    def bookmarks_for_area(self, area):
        cursor = self._db.execute("SELECT id, name, latitude, longitude, direction FROM bookmarks WHERE area = ?", (area,))
        marks = []
        for id, name, latitude, longitude, direction in cursor.fetchall():
            marks.append(Bookmark(id=id, name=name, latitude=latitude, longitude=longitude, area=area, direction=direction))
        return marks

    def _get_bookmark(self, area, name):
        res = self._db.execute("SELECT id, latitude, longitude, direction FROM bookmarks WHERE area = ? AND name = ?", (area, name))
        val = res.fetchone()
        if not val: return None
        id, latitude, longitude, direction = val
        return Bookmark(id=id, name=name, latitude=latitude, longitude=longitude, area=area, direction=direction)
    
    def remove_bookmark(self, bookmark_id):
        self._db.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self._db.commit()

    def last_location_for(self, area_id):
        return self._get_bookmark(area_id, LAST_LOCATION_NAME)
    
    def update_last_location_for(self, area_id, lat, lon, direction):
        location_id = self._last_location_ids.get(area_id, None)
        if location_id:
            self._db.execute("UPDATE bookmarks SET latitude=?, longitude=?, direction=? WHERE id = ?", (lat, lon, direction, location_id))
        else:
            self._db.execute("INSERT INTO bookmarks (area, name, latitude, longitude, direction) VALUES (?, ?, ?, ?, ?)", (area_id, LAST_LOCATION_NAME, lat, lon, direction))
            self._last_location_ids[area_id] = self._db.execute("SELECT id FROM bookmarks ORDER BY id DESC LIMIT 1").fetchone()[0]
        self._db.commit()

    def _table_has_column(self, table, column):
        res = self._db.execute(f"PRAGMA table_info({table})")
        for cid, name, type, notnull, default_value, pk in res.fetchall():
            if name == column:
                return True
        return False

    def _has_table(self, table):
        res = self._db.execute(f"PRAGMA table_info({table})")
        return len(res.fetchall()) > 0

    @property
    def _version(self):
        res = self._db.execute("SELECT max(version) FROM migrations")
        val = res.fetchone()[0]
        return val or 0

    def _migrate(self):
        ver = self._version
        if ver < 1:
            self._migrate_to_1()
        if ver < DB_VERSION:
            self._db.execute("INSERT INTO migrations (version, applied_at) VALUES (?, datetime())", (DB_VERSION,))
        self._db.commit()

    def _migrate_to_1(self):
        self._db.execute(MAYBE_CREATE_BOOKMARKS)
        if not self._table_has_column("bookmarks", "direction"):
            self._db.execute(ADD_DIRECTION_TO_BOOKMARKS)
        if self._has_table("last_locations"):
            if self._table_has_column("last_locations", "direction"):
                query = "INSERT INTO bookmarks SELECT NULL as id, ? as name, area as area, latitude as latitude, longitude as longitude, direction as direction from last_locations"
            else:
                query = "INSERT INTO bookmarks SELECT NULL as id, ? as name, area as area, latitude as latitude, longitude as longitude from last_locations"
            self._db.execute(query, (LAST_LOCATION_NAME,))
            self._db.execute("DROP TABLE last_locations")