from .generator import Generator
from shared.entities import Graveyard

class GraveyardGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Graveyard)
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "grave_yard"