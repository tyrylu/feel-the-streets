from .generator import Generator
from shared.models import PowerGenerator

class PowerGeneratorGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PowerGenerator)
        self.removes("power")
        self.unprefixes("generator")
        self.renames("generator:output:electricity", "electricity_output")
        self.renames("generator:output", "electricity_output") # And hope that both are never to be seen
        self.renames("generator:output:hot_water", "hot_water_output")
        self.renames("generator:output:steam", "steam_output")
        self.removes("building:ruian:type")
        

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "generator"