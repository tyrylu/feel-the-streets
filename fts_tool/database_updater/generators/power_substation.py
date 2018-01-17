from .generator import Generator
from shared.models import PowerSubstation

class PowerSubstationGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PowerSubstation)
        self.removes("power")
        self.renames("substation", "type")
        self.renames("building:levels", "building_levels")
        self.renames("roof:shape", "roof_shape")
        self.renames("building:colour", "building_colour")
        self.renames("roof:colour", "roof_colour")
        self.removes("building:ruian:type")

        self.renames("roof:levels", "roof_levels")
        self.renames("voltage-low", "low_voltage")
    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "substation"
