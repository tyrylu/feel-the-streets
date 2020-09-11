import logging, gc
from osm_db import EntitiesQuery, FieldNamed, AreaDatabase
from pygeodesy.ellipsoidalVincenty import LatLon
import shapely.wkb as wkb
from shapely.geometry.point import Point
from .geometry_utils import distance_filter, effective_width_filter, xy_ranges_bounding_square
from .measuring import measure
from .models import Bookmark, LastLocation
from .import services


log = logging.getLogger(__name__)

class Map:
    def __init__(self, map_id, map_name):
        self._id = map_id
        self._name = map_name
        self._db = AreaDatabase.open_existing(map_id, False)
        self._rough_distant_cache = None
    
    def intersections_at_position(self, position, fast=True):
        x, y = (position.lon, position.lat)
        query = EntitiesQuery()
        query.set_rectangle_of_interest(x, x, y, y)
        if fast:
            query.set_excluded_discriminators(["Route", "Boundary"])
        with measure("Retrieve candidates"):
            candidates = self._db.get_entities(query)
            candidate_ids = [e.id for e in candidates]
        effectively_inside = effective_width_filter(candidates, position)
        with measure("Intersection query"):
            intersecting = self._db.get_entities_really_intersecting(candidate_ids, x, y, fast)
            return list(intersecting) + effectively_inside
    
    def roughly_within_distance(self, position, distance, fast=True):
        if fast and self._rough_distant_cache is not None and self._rough_distant_cache[0] == position:
            return self._rough_distant_cache[1]
        min_x, min_y, max_x, max_y = xy_ranges_bounding_square(position, distance*2)
        query = EntitiesQuery()
        query.set_rectangle_of_interest(min_x, max_x, min_y, max_y)
        if fast:
            query.set_excluded_discriminators(["Boundary", "Route"])
        with measure("Index query"):
            rough_distant = self._db.get_entities(query)
        if fast:
            self._rough_distant_cache = (position, rough_distant)
        return rough_distant
    
    def within_distance(self, position, distance, fast=True):
        rough_distant = self.roughly_within_distance(position, distance, fast)
        entities = distance_filter(rough_distant, position, distance)
        log.debug("The distance filter decreased the count of entities from %s to %s.", len(rough_distant), len(entities))
        return entities

    def add_bookmark(self, name, lat, lon):
        bookmark = Bookmark(name=name, longitude=lon, latitude=lat, area=self._id)
        services.app_db_session().add(bookmark)
        services.app_db_session().commit()

    @property
    def bookmarks(self):
        return services.app_db_session().query(Bookmark).filter(Bookmark.area == self._id)

    def remove_bookmark(self, mark):
        services.app_db_session().delete(mark)
        services.app_db_session().commit()

    @property
    def _last_location_entity(self):
        return services.app_db_session().query(LastLocation).filter(LastLocation.area == self._id).first()

    @property
    def last_location(self):
        loc = self._last_location_entity
        if loc:
            return LatLon(loc.latitude, loc.longitude)
        else:
            return None

    @last_location.setter
    def last_location(self, val):
        loc = self._last_location_entity
        if not loc:
            loc = LastLocation(area=self._id)
            services.app_db_session().add(loc)
        loc.latitude = val.lat
        loc.longitude = val.lon
        services.app_db_session().commit()

    @property
    def default_start_location(self):
        query = EntitiesQuery()
        query.set_limit(1)
        query.set_included_discriminators(["Place"])
        query.add_condition(FieldNamed("name").eq(self._name))
        candidates =self._db.get_entities(query)
        if not candidates:
            log.warn("Area %s does not have a Place entity, falling back to the first entity in the database.", self._name)
            query = EntitiesQuery()
            query.set_limit(1)
            candidates = self._db.get_entities(query)
        entity = candidates[0]
        geom = wkb.loads(entity.geometry)
        if not isinstance(geom, Point):
            geom = geom.representative_point()
        lon = geom.x
        lat = geom.y
        return LatLon(lat, lon)
      
    def parents_of(self, entity):
        query = EntitiesQuery()
        query.set_parent_id(entity.id)
        return self._db.get_entities(query)
    def children_of(self, entity):
        query = EntitiesQuery()
        query.set_child_id(entity.id)
        return self._db.get_entities(query)

    def get_child_count(self, parent_id):
        return self._db.get_child_count(parent_id)

    def get_parent_count(self, child_id):
        return self._db.get_parent_count(child_id)

    def get_entities(self, query):
        #db = AreaDatabase.open_existing(self._id, server_side=False)
        return self._db.get_entities(query)