from .generator import Generator
from shared.models import BuildingPart

class BuildingPartGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(BuildingPart)
        self.renames("building:part", "type")
        self.renames("roof:shape", "roof_shape")
        self.renames("roof:direction", "roof_direction")
        self.renames("roof:height", "roof_height")
        self.renames("roof:material", "roof_material")
        self.renames("roof:orientation", "roof_orientation")
        self.removes("building:ruian:type")

        self.renames("roof:colour", "roof_colour")
        self.renames("roof:slope:direction", "roof_slope_direction")
        self.renames("building:material", "building_material")
    @staticmethod
    def accepts(props):
        return "building:part" in props
