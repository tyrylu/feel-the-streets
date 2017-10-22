from .building import BuildingGenerator
from shared.models import Castle

class CastleGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Castle)
        self.removes("historic")
        self.removes_subtree("castle_type")
        self.renames("castle_type", "type")
        self.removes_subtree("old_name")

    @staticmethod
    def accepts(props):
        return BuildingGenerator.accepts(props) and "historic" in props and props["historic"] == "castle"