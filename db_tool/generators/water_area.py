from .generator import Generator
from shared.models import WaterArea

class WaterAreaGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(WaterArea)
        self.removes("natural")
        self.renames("water", "type")

    @staticmethod
    def accepts(props):
        return ("type" in props and props["type"] == "water") or "water" in props