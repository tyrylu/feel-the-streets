from .amenity import AmenityGenerator
from shared.models import Cafe

class CafeGenerator(AmenityGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Cafe)
        self.renames("cafe", "cafe_type")

    @staticmethod
    def accepts(props):
        return AmenityGenerator.accepts(props) and "cafe" in props