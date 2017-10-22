from .generator import Generator
from shared.models import Pole

class PoleGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Pole)
        self.removes("power")
        self.renames("transformer", "transformer_type")

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "pole"