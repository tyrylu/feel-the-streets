from .generator import Generator
from shared.models import AerialWay

class AerialWayGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(AerialWay)
        self.renames("aerialway", "type")
        self.renames("aeroway", "type")
        self.renames("area:aeroway", "type")
        self.renames("disused:aeroway", "type")
        self.renames("roof:shape", "roof_shape")
        self.renames("bridge:structure", "bridge_structure")
        self.unprefixes("aerialway")
        self.removes_subtree("building:ruian")
        self.renames("aerodrome:type", "aerodrome_type")


        self.renames("disused:aeroway", "disused_aeroway")
        self.renames("note:cs", "note_cs")
        self.renames("beacon:type", "beacon_type")
        self.renames("building:levels", "building_levels")
    @staticmethod
    def accepts(props):
        return "aerialway" in props or "aeroway" in props or "aea:aeroway" in props or "disused:aeroway" in props
