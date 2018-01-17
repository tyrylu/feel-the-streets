from .generator import Generator
from shared.models import DemolishedBuilding

class DemolishedBuildingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(DemolishedBuilding)
        self.removes("demolished:building")

    @staticmethod
    def accepts(props):
        return "demolished:building" in props
