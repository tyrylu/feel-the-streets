from .generator import Generator
from shared.models import Barrier

class BarrierGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Barrier)
        self.renames("barrier", "type")
        self.renames("toll:hgv", "toll_hgv")
        self.removes("motor_vehicle:conditional")
        self.removes("access:conditional")
        self.removes("note:en")

    def _prepare_properties(self, entity_spec, props, record):
        props["barrier"] = props["barrier"].replace("-", "_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "barrier" in props and "tourism" not in props