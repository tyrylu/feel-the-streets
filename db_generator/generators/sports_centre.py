from .building import BuildingGenerator
from shared.models import SportsCentre

class SportsCentreGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(SportsCentre)
        self.removes("leisure")

    @staticmethod
    def accepts(props):
        return BuildingGenerator.accepts(props) and "leisure" in props and props["leisure"] in {"sports_centre", "stadium"}