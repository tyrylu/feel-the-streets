from .generator import Generator
from shared.models import Power

class PowerGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Power)
        self.renames("power", "type")
        self.renames("voltage-high", "high_voltage")
        self.renames("voltage-low", "low_voltage")

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] != "plant"