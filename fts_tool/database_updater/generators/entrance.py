from .generator import Generator
from shared.entities import Entrance

class EntranceGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Entrance)
        self.renames("entrance", "type")

    @staticmethod
    def accepts(props):
        return "entrance" in props or ("type" in props and props["type"] == "entrance")