from shared.entities import Crossing
from .generator import Generator

class CrossingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Crossing)
        self.renames("highway", "type")
        self.renames("crossing", "type")
        self.renames("traffic_signals:direction", "traffic_signals_direction")
        self.renames("traffic_signals:sound", "traffic_signals_sound")
        self.replaces_property_value("type", "; ", "_")
        self.renames("parking:lane:both", "both_parking_lane")
    @staticmethod
    def accepts(props):
        return "highway" in props and props["highway"] in {"crossing", "traffic_signals"}