from .generator import Generator
from shared.models import Graveyard

class GraveYardGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Graveyard)
        self.removes("amenity")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "grave_yard"