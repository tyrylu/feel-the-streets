import shapely.wkb as wkb
from sqlalchemy.orm import selectin_polymorphic
from shared.database import Database
import geoalchemy
from shared.models import Entity, IdxEntitiesGeometry
from shared.geometry_utils import xy_ranges_bounding_square, to_latlon, to_shapely_point, distance_between
from .geometry_utils import closest_point_to
from .measuring import measure

class Map:
    def __init__(self, map_name):
        self._db = Database(map_name)
    def intersections_at_position(self, position):
        x, y = (position.lon, position.lat)
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        return self._db.query(Entity).filter((Entity.id == IdxEntitiesGeometry.pkid) & (IdxEntitiesGeometry.xmin <= x) & (IdxEntitiesGeometry.xmax >= x) & (IdxEntitiesGeometry.ymin <= y) & (IdxEntitiesGeometry.ymax >= y))
    
    def within_distance(self, position, distance):
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        min_x, min_y, max_x, max_y = xy_ranges_bounding_square(position, distance*2)
        with measure("Index query"):
            rough_distant = list(self._db.query(Entity).filter((Entity.id == IdxEntitiesGeometry.pkid) & (IdxEntitiesGeometry.xmin <= max_x) & (IdxEntitiesGeometry.xmax >= min_x) & (IdxEntitiesGeometry.ymin <= max_y) & (IdxEntitiesGeometry.ymax >= min_y)))
        print("Rough distance query - %s results."%len(rough_distant))
        with measure("Pygeodesy filtering"):
            entities = []
            shapely_point = to_shapely_point(position)
            for entity in rough_distant:
                closest = closest_point_to(shapely_point, entity.geometry)
                closest_latlon = to_latlon(closest)
                cur_distance = distance_between(closest_latlon, position)
                if cur_distance <= distance:
                    entity.distance_from_current = cur_distance
                    entity.closest_point_to_current = closest_latlon
                    entities.append(entity)
    
        return entities

    def geometry_to_wkt(self, geometry):
        return wkb.loads(geometry.desc.desc).wkt

