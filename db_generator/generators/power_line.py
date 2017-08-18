from .generator import Generator
from shared.models import PowerLine

class PowerLineGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PowerLine)
        self.removes("power")

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "line"