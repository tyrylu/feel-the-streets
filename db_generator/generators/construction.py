from .generator import Generator
from shared.models import Construction

class ConstructionGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Construction)
        self.renames("construction", "type")

    @staticmethod
    def accepts(props):
        return "construction" in props