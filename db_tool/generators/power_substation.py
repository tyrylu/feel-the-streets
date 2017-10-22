from .generator import Generator
from shared.models import PowerSubstation

class PowerSubstationGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PowerSubstation)
        self.removes("power")
        self.renames("substation", "type")

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "substation"