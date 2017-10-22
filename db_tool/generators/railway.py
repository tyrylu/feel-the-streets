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
        self.renames("maxspeed:tilting", "tilting_maxspeed")
        self.renames("abandoned:railway", "abandoned_railway")
        self.renames("bridge:name", "bridge_name")
        self.renames("bridge:structure", "bridge_structure")
        self.renames("disused:railway", "disused_railway")
        self.removes_subtree("ruian")
        self.removes("maxspeed:source")
        self.unprefixes("building")
        self.unprefixes("railway")
        self.removes("railway:ref", True)
        self.removes("ref")
        self.removes("uic_ref")
    @staticmethod
    def accepts(props):
        return "railway" in props