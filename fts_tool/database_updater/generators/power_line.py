from .generator import Generator
from shared.models import PowerLine

class PowerLineGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PowerLine)
        self.renames("line", "type")
        self.removes("power")

        self.renames("line:colour", "line_colour")
    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] in {"line", "minor_line", "cable"} or "route" in props and props["route"] == "power"
