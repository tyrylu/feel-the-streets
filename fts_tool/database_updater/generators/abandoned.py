from .generator import Generator
from shared.entities import Abandoned

class AbandonedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Abandoned)
        self.renames("abandoned:highway", "type")

    @staticmethod
    def accepts(props):
        return "abandoned:highway" in props