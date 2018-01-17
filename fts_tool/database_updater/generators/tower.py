from .man_made import ManMadeGenerator
from shared.models import Tower

class TowerGenerator(ManMadeGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Tower)
        self.renames("tower:type", "tower_type")
        self.renames("building:part", "building_part")
        self.renames("communication:mobile_phone", "mobile_phone_communication")
        self.renames("tower:construction", "tower_construction")

        self.renames("building:colour", "colour")
        self.renames("roof:shape", "roof_shape")
        self.renames("building:material", "material")
        self.renames("building:levels", "levels")
        self.renames("roof:colour", "roof_colour")
        self.renames("building:flats", "flats")
        self.renames("communication:microwave", "microwave_communication")
        self.renames("communication:television", "television_communication")
    @staticmethod
    def accepts(props):
        return ManMadeGenerator.accepts(props) and (("man_made" in props and props["man_made"] == "tower") or ("razed:man_made" in props and props["razed:man_made"] == "tower") or ("tower:type" in props))
