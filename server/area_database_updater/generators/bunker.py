from .generator import Generator
from shared.entities import Bunker

class BunkerGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Bunker)
        self.renames("bunker_type", "type")

        self.renames("tower:type", "tower_type")
    @staticmethod
    def accepts(props):
        return "military" in props and props["military"] == "bunker"