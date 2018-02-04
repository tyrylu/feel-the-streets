from .generator import Generator
from shared.entities import Barrier

class BarrierGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Barrier)
        self.renames("barrier", "type")
        self.renames("toll:hgv", "toll_hgv")

        self.renames("lift_gate:type", "liftgate_type")
        self.renames("building:colour", "building_colour")
        self.renames("abandoned:highway", "abandoned_highway")
        self.renames("bridge:structure", "bridge_structure")
        self.renames("disused:railway", "disused_railway")
        self.renames("swing_gate:type", "swing_gate_type")
    def _prepare_properties(self, entity_spec, props, record):
        props["barrier"] = props["barrier"].replace("-", "_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "barrier" in props and "tourism" not in props