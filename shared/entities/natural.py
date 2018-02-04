import enum
from .enums import ManMade, TourismType, NaturalType, LandType, BarrierType, FenceType, GolfRelation, GardenType, SportType, HistoricType
from . import Named

class WetLandType(enum.Enum):
    bog = 0
    swamp = 1
    marsh = 2

class LeafCycle(enum.Enum):
    deciduous = 0
    evergreen = 1
    mixed = 2

class Natural(Named):
    type: NaturalType
    lining: str = None
    man_made: ManMade = None
    depth: float = None
    ele: float = None
    note: str = None
    drinking_water: bool = None
    alt_name: str = None
    website: str = None
    wikipedia: str = None
    inscription: str = None
    tourism_type: TourismType = None
    opening_hours: str = None
    surface: str = None
    material: str = None
    wikidata: str = None
    landuse: LandType = None
    barrier: BarrierType = None
    fence_type: FenceType = None
    leaf_type: str = None
    # Map them correctly to a tree
    golf: GolfRelation = None
    natural_1: NaturalType = None
    description: str = None
    layer: int = None
    uhul_area: str = None
    height: float = None
    uhul_slt: str = None
    garden_type: GardenType = None
    fixme: str = None
    sport: SportType = None
    landcover: str = None
    historic: HistoricType = None
    is_in: str = None
    wetland: WetLandType = None
    leaf_cycle: LeafCycle = None
    url: str = None
    import_ref: str = None
    wood: LeafCycle = None
