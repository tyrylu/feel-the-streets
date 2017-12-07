from .generator import Generator
from shared.models import Natural

class NaturalGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Natural)
        self.renames("natural", "type")
        self.renames("tourism", "tourism_type")


    @staticmethod
    def accepts(props):
        return "natural" in props