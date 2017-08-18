import logging
from .generator import Generator

log = logging.getLogger(__name__)
class NoOpGenerator(Generator):
    def generate_from(self, entity, is_way, record):
        if len(entity["properties"]) > 1:
            log.debug("Entity %s skipped as not having semantic meaning."%entity["properties"])
        return None

    @staticmethod
    def accepts(props):
        return True