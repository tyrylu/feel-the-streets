from .generator import Generator
from shared.models import Barrier

class BarrierGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Barrier)
        self.renames("barrier", "type")

    def _prepare_properties(self, entity_spec, props, record):
        props["barrier"] = props["barrier"].replace("-", "_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "barrier" in props and "tourism" not in props