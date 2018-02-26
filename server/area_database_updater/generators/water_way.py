from .generator import Generator
from shared.entities import WaterWay

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

        self.renames("whitewater:rapid_grade", "whitewater_rapid_grade")
        self.renames("seamark:notice:function", "seamark_notice_function")
        self.renames("seamark:type", "seamark_type")
        self.renames("seamark:notice:impact", "seamark_notice_impact")
        self.renames("seamark:notice:category", "seamark_notice_category")
    @staticmethod
    def accepts(props):
        return "waterway" in props