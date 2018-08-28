from inspect import isclass
import json
import logging
from .osm_object_manager import OSMObjectManager
from .generation_record import GenerationRecord
from .generators import Generator
from . import generators
from .json_encoding_utils import extended_types_encoder
from shared.models import Entity

log = logging.getLogger(__name__)
class OSMObjectTranslator:
    def __init__(self, use_cache, cache_responses):
        self.manager = OSMObjectManager(use_cache, cache_responses)
        self.record = GenerationRecord()
        self._generators = []
        for member in generators.__dict__.values():
            if isclass(member) and issubclass(member, Generator):
                self._generators.append(member)

    def translate_object(self, object):
        generator = self._lookup_generator(object.tags)
        if generator:
            generator_instance = generator()
            new_tags = generator_instance.generate_from(object, self.record)
            if new_tags:
                entity = Entity(data=json.dumps(new_tags, default=extended_types_encoder, ensure_ascii=False), discriminator=generator_instance._generates.__name__)
                return entity
    
    def translated_objects_in(self, area):
        log.info("Looking up all objects in area %s.", area)
        self.manager.lookup_objects_in(area)
        self.record.total_entities = self.manager.cached_total
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

    def _lookup_generator(self, props):
        for generator in self._generators:
            if generator.accepts(props):
                return generator