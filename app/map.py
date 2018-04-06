import shapely.wkb as wkb
from sqlalchemy import func
import geoalchemy
from shared.database import Database
from shared.geometry_utils import xy_ranges_bounding_square
from shared.models import Entity, IdxEntitiesGeometry
from .geometry_utils import distance_filter, effective_width_filter
from .measuring import measure
from .models import Bookmark
from .import services

class Map:
    def __init__(self, map_name):
        self._name = map_name
        self._db = Database(map_name, server_side=False)
    
    def intersections_at_position(self, position, fast=True):
        x, y = (position.lon, position.lat)
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        index_query = (IdxEntitiesGeometry.pkid == Entity.id) &( IdxEntitiesGeometry.xmin <= x) & (IdxEntitiesGeometry.xmax >= x) & (IdxEntitiesGeometry.ymin <= y) & (IdxEntitiesGeometry.ymax >= y)
        if fast:
            index_query = (Entity.discriminator != "Route") & index_query
        with measure("Retrieve candidates"):
            candidates = self._db.query(Entity).filter(index_query)
        candidate_ids = [e.id for e in candidates]
        effectively_inside = effective_width_filter(candidates, position)
        with measure("Intersection query"):
            intersection_query = Entity.id.in_(candidate_ids) & (Entity.geometry.gcontains(point))
            if fast:
                intersection_query = ((func.json_extract(Entity.data, "$.admin_level") > 8) | (func.json_extract(Entity.data, "$.admin_level") == None)) & intersection_query
            intersecting = self._db.query(Entity).filter(intersection_query)
            return list(intersecting) + effectively_inside
    
    def within_distance(self, position, distance, exclude_routes=True):
        min_x, min_y, max_x, max_y = xy_ranges_bounding_square(position, distance*2)
        query = (Entity.id == IdxEntitiesGeometry.pkid) & (IdxEntitiesGeometry.xmin <= max_x) & (IdxEntitiesGeometry.xmax >= min_x) & (IdxEntitiesGeometry.ymin <= max_y) & (IdxEntitiesGeometry.ymax >= min_y)
        if exclude_routes:
            query = (Entity.discriminator != "Route") & query
        with measure("Index query"):
            rough_distant = self._db.query(Entity).filter(query)
        entities = distance_filter(rough_distant, position, distance)
        return [e.create_osm_entity() for e in entities]

    def geometry_to_wkt(self, geometry):
        return wkb.loads(geometry.desc.desc).wkt


    def add_bookmark(self, name, lat, lon):
        bookmark = Bookmark(name=name, longitude=lon, latitude=lat, area=self._name)
        services.app_db_session().add(bookmark)
        services.app_db_session().commit()

    @property
    def bookmarks(self):
        return services.app_db_session().query(Bookmark).filter(Bookmark.area == self._name)

    def remove_bookmark(self, mark):
        services.app_db_session().delete(mark)
        services.app_db_session().commit()