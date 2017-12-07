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

    @staticmethod
    def accepts(props):
        return ManMadeGenerator.accepts(props) and (("man_made" in props and props["man_made"] == "tower") or ("razed:man_made" in props and props["razed:man_made"] == "tower") or ("tower:type" in props))