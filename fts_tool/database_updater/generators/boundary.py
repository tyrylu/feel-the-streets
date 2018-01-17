from .generator import Generator
from shared.models import Boundary

class BoundaryGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Boundary)
        self.renames("boundary", "type")
        self.renames("historic", "historic_type")
        self.renames("marker", "marker_type")
        self.renames("iso3166-2", "iso3166_2")
        self.renames("alt_name:de", "alt_name_de")
        self.renames("old_name:de", "odl_name_de")


        self.renames("tracktype", "track_type")
        self.renames("old_name:cs", "old_name_cs")
        self.renames("vehicle:conditional", "vehicle_conitional")
    @staticmethod
    def accepts(props):
        return "boundary" in props
