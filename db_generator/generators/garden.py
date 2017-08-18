from .leisure import LeisureGenerator
from shared.models import Garden

class GardenGenerator(LeisureGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Garden)
        self.renames("garden:type", "garden_type")

    @staticmethod
    def accepts(props):
        return LeisureGenerator.accepts(props) and props["leisure"] == "garden"