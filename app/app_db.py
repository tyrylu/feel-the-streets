import sqlite3
from .models import LastLocation, Bookmark

# Yes, the area columns could be integers, but only if we wouldn't mess the schema when migrating to area ids in the past (maybe before 1.0?).
MAYBE_CREATE_BOOKMARKS = "CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, area TEXT NOT NULL, name TEXT NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL, direction FLOAT NOT NULL DEFAULT 0.0);"
MAYBE_CREATE_LOCATIONS = "CREATE TABLE IF NOT EXISTS last_locations (id INTEGER PRIMARY KEY, area TEXT NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL, direction FLOAT NOT NULL DEFAULT 0.0);"
ADD_DIRECTION_TO_BOOKMARKS = "ALTER TABLE bookmarks ADD COLUMN direction FLOAT NOT NULL DEFAULT 0.0;"
ADD_DIRECTION_TO_LOCATIONS = "ALTER TABLE last_locations ADD COLUMN direction FLOAT NOT NULL DEFAULT 0.0;"

class AppDb:
    def __init__(self, db_path):
        self._db = sqlite3.connect(db_path)
        self._db.execute(MAYBE_CREATE_BOOKMARKS)
        self._db.execute(MAYBE_CREATE_LOCATIONS)
        if not self._table_has_column("bookmarks", "direction"):
            self._db.execute(ADD_DIRECTION_TO_BOOKMARKS)
        if not self._table_has_column("last_locations", "direction"):
            self._db.execute(ADD_DIRECTION_TO_LOCATIONS)
        res = self._db.execute("SELECT area, id from last_locations")
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

    def remove_bookmark(self, bookmark_id):
        self._db.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        self._db.commit()

    def last_location_for(self, area_id):
        cursor = self._db.execute("SELECT id, latitude, longitude, direction FROM last_locations where area = ? LIMIT 1", (area_id,))
        results = cursor.fetchall()
        if not results:
            return None
        id, latitude, longitude, direction = results[0]
        return LastLocation(id=id, area=area_id, latitude=latitude, longitude=longitude, direction=direction)

    def update_last_location_for(self, area_id, lat, lon, direction):
        location_id = self._last_location_ids.get(area_id, None)
        if location_id:
            self._db.execute("REPLACE INTO last_locations (id, area, latitude, longitude, direction) VALUES (?, ?, ?, ?, ?)", (location_id, area_id, lat, lon, direction))
        else:
            self._db.execute("INSERT INTO last_locations (area, latitude, longitude, direction) VALUES (?, ?, ?, ?)", (area_id, lat, lon, direction))
            self._last_location_ids[area_id] = self._db.execute("SELECT id FROM last_locations ORDER BY id DESC LIMIT 1").fetchone()[0]
        self._db.commit()

    def _table_has_column(self, table, column):
        res = self._db.execute(f"PRAGMA table_info({table})")
        for cid, name, type, notnull, default_value, pk in res.fetchall():
            if name == column:
                return True
        return False