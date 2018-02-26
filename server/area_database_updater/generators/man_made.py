from .generator import Generator
from shared.entities import ManMade

class ManMadeGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(ManMade)
        self.renames("razed:man_made", "type")
        self.renames("man_made", "type")
        self.unprefixes("contact")

        self.renames("wifi:ssid", "wifi_ssid")
        self.renames("building:material", "building_material")
        self.renames("note:en", "note_en")
        self.renames("monitoring:air_quality", "air_quality_monitoring")
    @staticmethod
    def accepts(props):
        return "razed:man_made" in props or "man_made" in props