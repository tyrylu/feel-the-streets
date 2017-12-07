from .generator import Generator
from shared.models import Entrance

class EntranceGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Entrance)
        self.renames("entrance", "type")
        self.removes("school") # It can be probably only an entrance, which is quite redundant there.

    @staticmethod
    def accepts(props):
        return "entrance" in props or ("type" in props and props["type"] == "entrance")