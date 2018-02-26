from .generator import Generator
from shared.entities import Place

class PlaceGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Place)
        self.renames("place", "type")
        self.renames("alt_name:de", "alt_name_de")
        self.unprefixes("contact")

        self.renames("wikipedia:cs", "wikipedia_cs")
        self.renames("alt_name:cs", "alt_name_cs")
    @staticmethod
    def accepts(props):
        return "place" in props