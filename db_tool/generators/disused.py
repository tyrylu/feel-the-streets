from .generator import Generator
from shared.models import Disused

class DisusedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Disused)
        self.renames("disused", "type")

    @staticmethod
    def accepts(props):
        return "disused" in props