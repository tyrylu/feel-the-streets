from . import Building
from .enums import GeneratorSource

class PowerPlant(Building):
    electricity_output: str = None
    frequency: int = None
    plant_source: GeneratorSource = None
