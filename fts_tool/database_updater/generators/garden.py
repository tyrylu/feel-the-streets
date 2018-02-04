from .leisure import LeisureGenerator
from shared.entities import Garden

class GardenGenerator(LeisureGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Garden)
        self.renames("garden:type", "garden_type")

    @staticmethod
    def accepts(props):
        return ("leisure" in props and props["leisure"] == "garden") or ("landuse" in props and props["landuse"] == "garden") or "garden:type" in props