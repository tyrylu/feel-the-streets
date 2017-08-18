from .generator import Generator
from shared.models import BuildingPart

class BuildingPartGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(BuildingPart)
        self.renames("building:part", "type")
        self.renames("roof:shape", "roof_shape")
        self.renames("roof:orientation", "roof_orientation")

    @staticmethod
    def accepts(props):
        return "building:part" in props