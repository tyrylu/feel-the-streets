from .generator import Generator
from shared.entities import DemolishedBuilding

class DemolishedBuildingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(DemolishedBuilding)

    @staticmethod
    def accepts(props):
        return "demolished:building" in props