from .amenity import AmenityGenerator
from shared.models import BicycleParking

class BicycleParkingGenerator(AmenityGenerator):
    def __init__(self):
        super().__init__()
        self.generates(BicycleParking)
        self.renames("bicycle_parking", "parking_type")
        self.renames("surveillance:type", "surveillance_type")
        self.renames("surveillance:zone", "surveillance_zone")

    @staticmethod
    def accepts(props):
        return AmenityGenerator.accepts(props) and "bicycle_parking" in props