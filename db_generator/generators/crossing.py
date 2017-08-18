from shared.models import Crossing
from .generator import Generator

class CrossingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Crossing)
        self.renames("highway", "type")
        self.removes("crossing_ref")
        self.renames("crossing", "type")
        self.removes_subtree("maxheight")
        self.replaces_property_value("type", "; ", "_")
    @staticmethod
    def accepts(props):
        return "highway" in props and props["highway"] in {"crossing", "traffic_signals"}