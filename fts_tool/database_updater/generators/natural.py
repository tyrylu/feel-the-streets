from .generator import Generator
from shared.models import Natural

class NaturalGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Natural)
        self.renames("natural", "type")
        self.renames("tourism", "tourism_type")


        self.renames("uhul:area", "uhul_area")
        self.renames("uhul:slt", "uhul_slt")
        self.renames("garden:type", "garden_type")
    @staticmethod
    def accepts(props):
        return "natural" in props
