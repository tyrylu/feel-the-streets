import sys
import time
import logging
import geoalchemy.functions as gf
from geoalchemy import WKTSpatialElement
import shapely.wkt
from shared.database import Database
from .osm_object_translator import OSMObjectTranslator
from .utils import get_srid_from_point

log = logging.getLogger(__name__)

class DatabaseUpdater:
    def __init__(self, location, check_geometries, use_cache, cache_responses):
        self._location = location
        self.translator = OSMObjectTranslator(use_cache, cache_responses)
        self._db = Database(location)
        self._check_geoms = check_geometries
        self._assigned_id = 1
        self._db.create_if_needed()

    def entities_in_location(self, check_geometry_size=False):
        for entity, object in self.translator.translated_objects_in(self._location):
            geometry = self.translator.manager.get_geometry_as_wkt(object)
            geom_size = len(geometry)
            if check_geometry_size and geom_size > 1000000:
                log.warn("Skipping object with tags %s because of the excessively huge geometry of size %s.", object.tags, geom_size)
                continue
            if not geometry:
                log.error("Failed to generate geometry for %s.", object)
                continue
            if self._check_geoms:
                try:
                    shapely.wkt.loads(geometry)
                except Exception as exc:
                    log.error("Failed to parse geometry of %s, error %s.", object, exc)
                    continue
            entity.geometry = WKTSpatialElement(geometry)
            self._maybe_polygonize(entity)
            entity.id = self._assigned_id
            self._assigned_id += 1
            yield entity
        self.translator.record.save_to_file("generation_record_%s.txt"%self._location)
        self.translator.record.save_to_pickle("%s.grd"%self._location)
        
    def update_database(self, exclude_huge=False):
        for entity in self.entities_in_location(exclude_huge):
            self._db.schedule_entity_addition(entity)
        self._db.add_entities()

    def _maybe_polygonize(self, entity):
        if hasattr(entity, "effective_width") and entity.effective_width > 0 and entity.geometry.geom_wkt.startswith("LINESTRING"):
            entity.original_geometry = entity.geometry
            log.debug("Creating containment polygon for entity %s.", entity.id)
            x = self._db.scalar(entity.original_geometry.point_n(1).x())
            y = self._db.scalar(entity.original_geometry.point_n(1).y())
            entity.geometry = WKTSpatialElement(self._db.scalar(entity.original_geometry.transform(get_srid_from_point(x, y)).buffer(entity.effective_width).transform(4326).wkt()))
        return entity

