import sqlite3
from .models import LastLocation, Bookmark

# Yes, the area columns could be integers, but only if we wouldn't mess the schema when migrating to area ids in the past (maybe before 1.0?).
MAYBE_CREATE_BOOKMARKS = "CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, area TEXT NOT NULL, name TEXT NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL);"
MAYBE_CREATE_LOCATIONS = "CREATE TABLE IF NOT EXISTS last_locations (id INTEGER PRIMARY KEY, area TEXT NOT NULL, latitude FLOAT NOT NULL, longitude FLOAT NOT NULL);"

class AppDb:
    def __init__(self, db_path):
        self._db = sqlite3.connect(db_path)
        self._db.execute(MAYBE_CREATE_BOOKMARKS)
        self._db.execute(MAYBE_CREATE_LOCATIONS)

    def add_bookmark(self, mark):
        self._db.execute("INSERT INTO bookmarks (name, area, latitude, longitude), VALUES (?, ?, ?, ?)", (makr.name, mark.area, mark.latitude, mark.longitude))

    def bookmarks_for_area(self, area):
        cursor = self._db.execute("SELECT id, name, latitude, longitude FROM bookmarks WHERE area = ?", (area,))
        marks = []
        for id, name, latitude, longitude in cursor.fetchall():
            marks.append(Bookmark(id=id, name=name, latitude=latitude, longitude=longitude, area=area))
        return marks

    def remove_bookmark(self, bookmark_id):
        self._db.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))

    def last_location_for(self, area_id):
        cursor = self._db.execute("SELECT id, latitude, longitude FROM last_locations where area = ? LIMIT 1", (area_id,))
        results = cursor.fetchall()
        if not results:
            return None
        id, latitude, longitude = results[0]
        return LastLocation(id=id, area=area_id, latitude=latitude, longitude=longitude)

    def update_last_location_for(self, area_id, lat, lon):
        self._db.execute("REPLACE INTO last_locations (area, latitude, longitude) VALUES (?, ?, ?)", (area_id, lat, lon))