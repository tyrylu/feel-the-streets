from .generator import Generator
from shared.models import Road

class FordGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Road)
        self.removes("ford")

    def _prepare_properties(self, entity_spec, props, record):
        props = super()._prepare_properties(entity_spec, props, record)
        props["type"] = "ford"
        return props
    @staticmethod
    def accepts(props):
        return "ford" in props