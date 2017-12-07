from .generator import Generator
from shared.models import WaterWay

class WaterWayGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(WaterWay)
        self.renames("waterway", "type")
        self.renames("boat", "boats_allowed")
        self.renames("motorboat", "motor_boats_allowed")
        self.renames("mtb:scale", "mtb_scale")
        self.renames("whitewater:section_grade", "whitewater_section_grade")
        self.renames("whitewater:section_name", "whitewater_section_name")
        self.renames("whitewater:rapid_name", "whitewater_rapid_name")
        self.renames("life_cycle:start_date", "start_date")
        self.removes("vehicle:conditional")

    @staticmethod
    def accepts(props):
        return "waterway" in props