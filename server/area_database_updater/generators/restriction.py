from .generator import Generator
from shared.entities import Restriction

class RestrictionGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Restriction)
        self.renames("restriction", "type")
        self.renames("except", "except_")

        self.renames("restriction:hgv", "hgv_restriction")
        self.renames("restriction:conditional", "conditional")
    @staticmethod
    def accepts(props):
        return "type" in props and props["type"] == "restriction"