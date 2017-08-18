from .generator import Generator
from shared.models import Boundary

class BoundaryGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Boundary)
        self.renames("boundary", "type")
        self.renames("historic", "historic_type")
        self.renames("marker", "marker_type")
        

    @staticmethod
    def accepts(props):
        return "boundary" in props