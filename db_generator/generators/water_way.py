from .generator import Generator
from shared.models import WaterWay

class WaterWayGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(WaterWay)
        self.renames("waterway", "type")
        self.renames("boat", "boats_allowed")
        self.renames("motorboat", "motor_boats_allowed")
        self.removes("vehicle:conditional")

    @staticmethod
    def accepts(props):
        return "waterway" in props