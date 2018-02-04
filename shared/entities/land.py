import enum
from .enums import ShopType, ManMade, BarrierType, NaturalType, LeisureType, LandType, ConstructionType, IndustrialType, Surface, FenceType, AccessType, BridgeStructure, LandCover, ResidentialType, SiteType, Denomination, MilitaryType
from . import Named, Address

class Trees(enum.Enum):
    cherry_trees = 0
    apple_trees = 1

class MeadowType(enum.Enum):
    none = 0
    agricultural = 1
    pasture = 2
    perpetual = 3

class BasinType(enum.Enum):
    detention = 0
    retention = 1
    infiltration = 2

class PlantType(enum.Enum):
    tree = 0

class DepotType(enum.Enum):
    bus = 0
    tram = 1
    subway = 2

class Land(Named):
    type: LandType
    shop_type: ShopType = None
    website: str = None
    meadow_type: MeadowType = None
    man_made: ManMade = None
    crop: str = None
    barrier: BarrierType = None
    note: str = None
    comment: str = None
    natural_type: NaturalType = None
    military_type: MilitaryType = None
    operator: str = None
    resource: str = None
    leisure: LeisureType = None
    address: Address = None
    leaf_cycle: str = None
    religion: str = None
    wikidata: str = None
    wikipedia: str = None
    landcover: LandCover = None
    description: str = None
    opening_hours: str = None
    disused: bool = None
    abandoned: bool = None
    layer: int = None
    construction: ConstructionType = None
    old_name: str = None
    industrial: IndustrialType = None
    basin: BasinType = None
    # Separate entity?
    alt_name: str = None
    fence_type: FenceType = None
    fixme: str = None
    loc_name: str = None
    residential: ResidentialType = None
    surface: Surface = None
    plant: PlantType = None
    uhul_slt: str = None
    is_in: str = None
    access: AccessType = None
    leaf_type: str = None
    # Find out why it is there and make it an enumerate
    start_date: str = None
    uhul_area: str = None
    uhul_id: str = None
    wood: str = None
    # And again, why it is there?
    landuse_1: LandType = None
    ele: float = None
    id_fb: int = None
    fenced: bool = None
    depot: DepotType = None
    # Separate entity?
    sorting_name: str = None
    height: float = None
    trees: Trees = None
    reservoir_type: str = None
    # Separate entity?
    genus: str = None
    bridge_structure: BridgeStructure = None
    level: int = None
    finely_mown: bool = None
    golf: str = None
    # Separate entity?
    mown: bool = None
    email: str = None
    phone: str = None
    colour: str = None
    barrier_height: float = None
    denomination: Denomination = None
    clc_code: int = None
    site_type: SiteType = None
