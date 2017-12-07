import logging
from .generator import Generator

log = logging.getLogger(__name__)
class NoOpGenerator(Generator):
    def generate_from(self, entity, record):
        if ("parent_id" in entity.tags and len(entity.tags) > 3) or len(entity.tags) > 1:
            log.debug("Entity %s skipped as not having semantic meaning.", entity)
        return None

    @staticmethod
    def accepts(props):
        return True