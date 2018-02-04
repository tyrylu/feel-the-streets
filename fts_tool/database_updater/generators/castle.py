from .building import BuildingGenerator
from shared.entities import Castle

class CastleGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Castle)
        self.renames("castle_type", "type")

    @staticmethod
    def accepts(props):
        return BuildingGenerator.accepts(props) and "historic" in props and props["historic"] == "castle"