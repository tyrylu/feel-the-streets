from .building import BuildingGenerator
from shared.models import PowerPlant

class PowerPlantGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(PowerPlant)
        self.removes("power")
        self.renames("plant:output:electricity", "electricity_output")
        

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "plant"