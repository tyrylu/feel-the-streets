import logging
import os
from geoalchemy import WKTSpatialElement
import shapely.wkt
from shared.database import Database
from .osm_object_translator import OSMObjectTranslator

log = logging.getLogger(__name__)

class DatabaseUpdater:
    def __init__(self, location, use_cache, cache_responses):
        self._location = location
        self.translator = OSMObjectTranslator(use_cache, cache_responses)
        self._db = Database(location)
        self._assigned_id = 1
        self._db.create_if_needed()

    def entities_in_location(self, check_geometry_size=False):
        for entity, object in self.translator.translated_objects_in(self._location):
            geometry = self.translator.manager.get_geometry_as_wkt(object)
            geom_size = len(geometry)
            if check_geometry_size and geom_size > 1000000:
                log.warning("Skipping object with tags %s because of the excessively huge geometry of size %s.", object.tags, geom_size)
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
        
    def create_database(self, exclude_huge=False):
        self._db.prepare_entity_insertions()
        for entity in self.entities_in_location(exclude_huge):
            self._db.insert_entity(entity)
        log.info("Committing the insertion transaction.")
        self._db.commit_entity_insertions()

    def _ensure_valid_geometry(self, geometry):
        if "EMPTY" in geometry:
            return None
        if geometry.startswith("POINT") or geometry.startswith("LINESTRING"):
            return geometry
        try:
            sh_geom = shapely.wkt.loads(geometry)
            if not sh_geom.is_valid:
                log.debug("Invalid geometry %s.", geometry)
                sh_geom = sh_geom.buffer(0)
                if not sh_geom.is_valid or "EMPTY" in sh_geom.wkt:
                    log.error("Zero buffer failed to fix the entity geometry validity.")
                    return None
        except Exception as exc:
            log.error("Failed to parse geometry %s, error %s.", geometry, exc)
            return None
        return sh_geom.wkt