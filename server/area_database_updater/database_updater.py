import logging
import os
from geoalchemy import WKTSpatialElement
from shared.database import Database
from .osm_object_translator import OSMObjectTranslator
from .utils import ensure_valid_geometry
from .osm_object_blacklist import OSMObjectBlacklist

log = logging.getLogger(__name__)

class DatabaseUpdater:
    def __init__(self, location, use_cache, cache_responses):
        self._location = location
        self.translator = OSMObjectTranslator(use_cache, cache_responses)
        self._db = Database(location)
        self._assigned_id = 1
        self._blacklist = OSMObjectBlacklist()
        self._db.create_if_needed()

    def entities_in_location(self, check_geometry_size=False):
        for entity, object in self.translator.translated_objects_in(self._location):
            if check_geometry_size and object.unique_id in self._blacklist:
                log.info("Skipping object %s because of its inclusion on the blacklist.", object.unique_id)
                continue
            geometry = self.translator.manager.get_geometry_as_wkt(object)
            geom_size = len(geometry)
            if check_geometry_size and geom_size > 1000000:
                log.warning("Skipping object with tags %s because of the excessively huge geometry of size %s.", object.tags, geom_size)
                self._blacklist.add(object.unique_id)
                continue
            geometry = ensure_valid_geometry(geometry)
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
        self._blacklist.save()
        
    def create_database(self, exclude_huge=False):
        self._db.prepare_entity_insertions()
        for entity in self.entities_in_location(exclude_huge):
            self._db.insert_entity(entity)
        log.info("Committing the insertion transaction.")
        self._db.commit_entity_insertions()
        self._db.close()