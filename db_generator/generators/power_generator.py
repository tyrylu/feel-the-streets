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
        

    @staticmethod
    def accepts(props):
        return "power" in props and props["power"] == "generator"