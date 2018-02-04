from .generator import Generator
from shared.entities import Recycling

class RecyclingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Recycling)
        self.renames("recycling_type", "type")
        self.unprefixes("recycling")
        self.renames("telephone", "phone")
        self.unprefixes("contact")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "recycling" or "recycling_type" in props