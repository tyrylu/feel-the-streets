from shared.database import Database
import geoalchemy
from shared.models import Entity

class Map:
    def __init__(self, map_name):
        self._db = Database(map_name)
    def intersections_at_position(self, position):
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        return self._db.query(Entity).filter(Entity.geometry.intersects(point))
    
    def within_distance(self, position, distance):
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        return self._db.query(Entity).filter(Entity.geometry.distance(point, 1) <= distance)

    def geometry_to_wkt(self, geometry):
        return self._db.scalar(geometry.wkt())