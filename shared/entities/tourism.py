import enum
from .enums import TourismType, SmokingType, BarrierType, InfoType, ManMade, HistoricType, Amenity, BuildingType, NaturalType, BuildingPartType, RoofShape, WheelchairAccess, AccessType, LeisureType, Location, AttractionType, MemorialKind, PlaceType, Surface, IndoorType, LandType, Support, ArtWorkType
from . import Addressable

class Denotation(enum.Enum):
    natural_monument = 0

class WaterSlideType(enum.Enum):
    body_slide = 0

class ShowerType(enum.Enum):
    hot = 0

class Tourism(Addressable):
    type: TourismType
    operator: str = None
    information_type: InfoType = None
    hiking: bool = None
    bicycle: bool = None
    stars: int = None
    map_type: str = None
    map_size: str = None
    ski: bool = None
    fireplace: bool = None
    artist_name: str = None
    artwork_type: ArtWorkType = None
    start_date: str = None
    smoking: SmokingType = None
    phone: str = None
    wikipedia: str = None
    barrier_type: BarrierType = None
    direction: str = None
    material: str = None
    inscription: str = None
    foot: bool = None
    zoo: str = None
    height: int = None
    man_made: ManMade = None
    historic: HistoricType = None
    amenity: Amenity = None
    building: BuildingType = None
    natural: NaturalType = None
    cuisine: str = None
    building_part: BuildingPartType = None
    internet_access_fee: bool = None
    roof_height: int = None
    roof_shape: RoofShape = None
    heritage: int = None
    heritage_operator: str = None
    fee: bool = None
    old_name: str = None
    designation: str = None
    rooms: int = None
    image: str = None
    wheelchair: WheelchairAccess = None
    access: AccessType = None
    disused: bool = None
    layer: int = None
    architect: str = None
    leisure: LeisureType = None
    bitcoin_payment: bool = None
    noname: bool = None
    attraction: AttractionType = None
    religion: str = None
    caravans: bool = None
    tents: bool = None
    en_description: str = None
    facebook: str = None
    species: str = None
    # What they do there?
    taxon_cs: str = None
    fax: str = None
    short_name: str = None
    ref_1: str = None
    min_height: int = None
    location: Location = None
    denotation: Denotation = None
    leaf_type: str = None
    # Why is it here?
    taxon: str = None
    official_name: str = None
    colour: str = None
    lit: bool = None
    artwork_subject: str = None
    author: str = None
    artist_wikidata: str = None
    memorial: MemorialKind = None
    support: Support = None
    place: PlaceType = None
    surface: Surface = None
    power_supply: bool = None
    indoor: IndoorType = None
    breakfast: bool = None
    covered: bool = None
    flood_date: str = None
    horse: bool = None
    artist: str = None
    en_note: str = None
    water_slide: WaterSlideType = None
    landuse: LandType = None
    shower: ShowerType = None
    litecoin_payment: bool = None
    high_water_height: int = None
    drinking_water: bool = None
    noexit: bool = None
    old_ref: str = None
    alt_name_cs: str = None
