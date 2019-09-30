import osm_db
import shapely.wkb as wkb
from sqlalchemy import func, literal_column
import geoalchemy
from pygeodesy.ellipsoidalVincenty import LatLon
from shared.geometry_utils import xy_ranges_bounding_square
from .geometry_utils import distance_filter, effective_width_filter
from .measuring import measure
from .models import Bookmark, LastLocation
from .import services

class Map:
    def __init__(self, map_name):
        self._name = map_name
        self._db = osm_db.AreaDatabase.open_existing(map_name, False)
    
    def intersections_at_position(self, position, fast=True):
        x, y = (position.lon, position.lat)
        point = geoalchemy.WKTSpatialElement("POINT(%s %s)"%(position.lon, position.lat))
        query = osm_db.EntitiesQuery()
        query.set_rectangle_of_interest(x, x, y, y)
        if fast:
            query.set_excluded_discriminators(["Route"])
        with measure("Retrieve candidates"):
            candidates = self._db.get_entities(query)
        candidate_ids = [e.id for e in candidates]
        print(len(candidate_ids))
        effectively_inside = effective_width_filter(candidates, position)
        with measure("Intersection query"):
            intersecting = self._db.get_entities_really_intersecting(candidate_ids, x, y, fast)
            print(intersecting)
            return list(intersecting) + effectively_inside
    
    def within_distance(self, position, distance, exclude_routes=True):
        min_x, min_y, max_x, max_y = xy_ranges_bounding_square(position, distance*2)
        # Can be replaced by an EntityQuery
        query = osm_db.EntitiesQuery()
        query.set_rectangle_of_interest(min_x, max_x, min_y, max_y)
        if exclude_routes:
            query.set_excluded_discriminators(["Route"])
        with measure("Index query"):
            rough_distant = self._db.get_entities(query)
        entities = distance_filter(rough_distant, position, distance)
        return entities

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

    @property
    def _last_location_entity(self):
        return services.app_db_session().query(LastLocation).filter(LastLocation.area == self._name).first()

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
            loc = LastLocation(area=self._name)
            services.app_db_session().add(loc)
        loc.latitude = val.lat
        loc.longitude = val.lon
        services.app_db_session().commit()