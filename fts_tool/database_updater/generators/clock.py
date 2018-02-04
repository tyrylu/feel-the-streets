from .amenity import AmenityGenerator
from shared.entities import Clock

class ClockGenerator(AmenityGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Clock)

    @staticmethod
    def accepts(props):
        return AmenityGenerator.accepts(props) and props["amenity"] == "clock"