from .building import BuildingGenerator
from shared.entities import PowerPlant

class PowerPlantGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(PowerPlant)
        self.renames("plant:output:electricity", "electricity_output")


        self.renames("plant:source", "plant_source")
    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "plant"