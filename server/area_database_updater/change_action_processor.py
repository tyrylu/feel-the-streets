import json
import logging
from .osm_change import OSMChangeType
from .osm_object_translator import OSMObjectTranslator
from shared.semantic_change import Change, ChangeType
from shared.diff_utils import DictChange, diff
from shared import Database

log = logging.getLogger(__name__)
class ChangeActionProcessor:

    def __init__(self, location):
        self._location = location
        self._db = Database(location)
        self._translator = OSMObjectTranslator(False, False)
        self._newest_timestamp = None

    def new_semantic_changes(self, date=None):
        self._newest_timestamp = "1970-01-01"
        if not date:
            date = self._db.last_timestamp
        num = 0
        for action in self._translator.manager.lookup_differences_in(self._location, date):
            if action.new and action.new.timestamp > self._newest_timestamp:
                self._newest_timestamp = action.new.timestamp
            num += 1
            if action.type is OSMChangeType.delete and self._db.has_entity(action.old.unique_id):
                yield self._gen_entity_deletion_change(action.old)
            elif action.type is OSMChangeType.create:
                change = self._gen_entity_creation_change(action.new)
                if change:
                    yield change
            elif action.type is OSMChangeType.modify:
                change = self._gen_entity_modification_change(action)
                if change:
                    yield change
        log.info("Processed %s osm object changes.", num)
    
    def _gen_entity_deletion_change(self, entity):
            return Change(osm_id=entity.unique_id, type=ChangeType.delete)
    
    def _gen_entity_creation_change(self, entity):
        db_entity = self._translator.translate_object(entity)
        if not db_entity:
            return
        change = Change(type=ChangeType.create, osm_id=entity.unique_id)
        change.property_changes.append(DictChange.creating("data", db_entity.data))
        change.property_changes.append(DictChange.creating("discriminator", db_entity.discriminator))
        width = db_entity.create_osm_entity().effective_width
        change.property_changes.append(DictChange.creating("effective_width", width))
        geometry = self._translator.manager.get_geometry_as_wkt(entity)
        change.property_changes.append(DictChange.creating("geometry", geometry))
        return change

    def _gen_entity_modification_change(self, action):
        old_entity = self._db.get_entity_by_osm_id(action.old.unique_id)
        new_entity = self._translator.translate_object(action.new)
        if not old_entity and new_entity:
            return self._gen_entity_creation_change(action.new)
        elif old_entity and not new_entity:
            return self._gen_entity_deletion_change(action.old)
        elif not old_entity and not new_entity:
            return None
        old_props, old_data = self._reconstruct_properties_and_data(action.old, old_entity)
        new_props, new_data = self._reconstruct_properties_and_data(action.new, new_entity)
        change = Change(osm_id=action.old.unique_id, type=ChangeType.update)
        change.property_changes = diff(old_props, new_props)
        change.data_changes = diff(old_data, new_data)
        return change

    def _reconstruct_properties_and_data(self, entity, db_entity):
        data = json.loads(db_entity.data)
        props = {}
        props["discriminator"] = db_entity.discriminator
        props["effective_width"] = db_entity.create_osm_entity().effective_width
        if db_entity.geometry:
            props["geometry"] = self._db.scalar(db_entity.geometry.wkt)
        else:
            props["geometry"] = self._translator.manager.get_geometry_as_wkt(entity)
        return props, data

    @property
    def newest_timestamp(self):
        return self._newest_timestamp