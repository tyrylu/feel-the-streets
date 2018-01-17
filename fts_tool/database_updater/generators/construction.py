from .generator import Generator
from shared.models import Construction

class ConstructionGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Construction)
        self.renames("construction", "type")
        self.renames("abandoned:highway", "abandoned_highway")
        self.renames("abandoned:ref", "abandoned_ref")
        self.renames("official_name:en", "official_en_name")

    @staticmethod
    def accepts(props):
        return "construction" in props
