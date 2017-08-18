from .address_aware import AddressAwareGenerator
from shared.models import RailWay

class RailWayGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(RailWay)
        self.renames("railway", "type")
        self.renames("bridge", "is_bridge")
        self.renames("crossing:light", "crossing_light")
        self.renames("crossing:bell", "crossing_bell")
        self.renames("crossing:barrier", "crossing_barrier")
        self.renames("crossing", "crossing_type")
        self.renames("building", "building_type")
        self.renames("oneway:tram", "tram_oneway")
        self.removes_subtree("ruian")
        self.unprefixes("building")
        self.unprefixes("railway")
        self.removes("railway:ref", True)
        self.removes("ref")
        self.removes("uic_ref")
    @staticmethod
    def accepts(props):
        return "railway" in props