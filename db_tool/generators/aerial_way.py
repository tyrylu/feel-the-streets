from .generator import Generator
from shared.models import AerialWay

class AerialWayGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(AerialWay)
        self.renames("aerialway", "type")
        self.renames("aeroway", "type")
        self.renames("roof:shape", "roof_shape")
        self.renames("bridge:structure", "bridge_structure")
        self.unprefixes("aerialway")
        self.removes_subtree("building:ruian")
        self.renames("aerodrome:type", "aerodrome_type")
        

    @staticmethod
    def accepts(props):
        return "aerialway" in props or "aeroway" in props