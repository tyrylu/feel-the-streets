from .generator import Generator
from shared.entities import Road
from shared.entities.enums import RoadType

class FordGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Road)

    def _prepare_properties(self, entity_spec, props, record):
        props = super()._prepare_properties(entity_spec, props, record)
        props["type"] = RoadType.ford
        return props
    @staticmethod
    def accepts(props):
        return "ford" in props