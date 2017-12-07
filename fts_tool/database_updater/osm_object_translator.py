import logging
import inspect
from . import generators
from .generators.generator import Generator
from .osm_object_manager import OSMObjectManager
from .generation_record import GenerationRecord

log = logging.getLogger(__name__)
class OSMObjectTranslator:
    def __init__(self, use_cache, cache_responses):
        self.manager = OSMObjectManager(use_cache, cache_responses)
        self.record = GenerationRecord()
        self._generators = []
        for member in generators.__dict__.values():
            if inspect.isclass(member) and issubclass(member, Generator):
                self._generators.append(member)
        
    def translate_object(self, object):
        for member in self._generators:
            if member.accepts(object.tags):
                instance = member()
                return instance.generate_from(object, self.record)

    def translated_objects_in(self, area):
        log.info("Looking up all objects in area %s.", area)
        self.manager.lookup_objects_in(area)
        self.record.total_entities = self.manager.cached_relations + self.manager.cached_ways + self.manager.cached_nodes
        log.info("Translating relations.")
        for rel in self.manager.relations:
            entity = self.translate_object(rel)
            if entity:
                self.record.processed_entities += 1
                yield entity, rel
        log.info("Translating ways.")
        for way in self.manager.ways:
            entity = self.translate_object(way)
            if entity:
                self.record.processed_entities += 1
                yield entity, way
        log.info("Translating nodes.")
        for node in self.manager.nodes:
            entity = self.translate_object(node)
            if entity:
                self.record.processed_entities += 1
                yield entity, node
