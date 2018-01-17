from .generator import Generator
from shared.models import Disused

class DisusedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Disused)
        self.renames("disused", "type")
        self.renames("destroyed:amenity", "destroyed_amenity")
        self.renames("destroyed:name", "destroyed_name")

        self.renames("disused:highway", "highway")
        self.renames("disused:name", "name")
    @staticmethod
    def accepts(props):
        return "disused" in props or "disused:amenity" in props
