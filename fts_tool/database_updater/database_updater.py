import sys
import time
import logging
import os
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
            geometry = self._ensure_valid_geometry(geometry)
            if not geometry:
                log.error("Failed to generate geometry for %s.", object)
                continue

            entity.geometry = WKTSpatialElement(geometry)
            osm_entity = entity.create_osm_entity()
            if hasattr(osm_entity, "effective_width"):
                entity.effective_width = osm_entity.effective_width
            entity.id = self._assigned_id
            self._assigned_id += 1
            yield entity
        os.makedirs("generation_records", exist_ok=True)
        self.translator.record.save_to_file(os.path.join("generation_records", "%s.txt"%self._location))
        self.translator.record.save_to_pickle(os.path.join("generation_records", "%s.grd"%self._location))
        
    def update_database(self, exclude_huge=False):
        for entity in self.entities_in_location(exclude_huge):
            self._db.schedule_entity_addition(entity)
        self._db.add_entities()

    def _ensure_valid_geometry(self, geometry):
        if geometry.startswith("POINT") or geometry.startswith("LINESTRING"):
            return geometry
        try:
            sh_geom = shapely.wkt.loads(geometry)
            if not sh_geom.is_valid:
                log.debug("Invalid geometry %s.", geometry)
                sh_geom = sh_geom.buffer(0)
                if not sh_geom.is_valid:
                    log.error("Zero buffer failed to fix the entity validity.")
                    return None
            else:
                log.info("Geometry valid.")
        except Exception as exc:
            log.error("Failed to parse geometry %s, error %s.", geometry, exc)
            return None
        return sh_geom.wkt