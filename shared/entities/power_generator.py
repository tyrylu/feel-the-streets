import enum
from . import Named
from .enums import BuildingType, BarrierType, GeneratorSource

class GeneratorType(enum.Enum):
    unknown = 0
    kaplan_turbine = 1
    solar_photovoltaic_panel = 2
    combined_cycle = 3
    
class PowerGenerator(Named):
    source: GeneratorSource = None
    type: GeneratorType = None
    electricity_output: str = None
    method: str = None
    building: BuildingType = None
    hot_water_output: str = None
    frequency: int = None
    operator: str = None
    start_date: str = None
    steam_output: str = None
    layer: int = None
    barrier: BarrierType = None
    note: str = None
