import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import TourismType, SmokingType, BarrierType, InfoType, ManMade, HistoricType, Amenity, BuildingType, NaturalType, BuildingPartType, RoofShape, OSMObjectType, WheelchairAccess, AccessType, LeisureType
from . import Addressable

class ArtWorkType(enum.Enum):
    none = 0
    statue = 1
    sculpture = 2
    mural = 3
    topiary = 4
    tower = 5
    photo = 6
    relief = 7
    architecture = 8
    installation = 9

class AttractionType(enum.Enum):
    animal = 0
class Tourism(Addressable):
    __tablename__ = "tourisms"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'tourism'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(TourismType), nullable=False)
    operator = Column(UnicodeText)
    information_type = Column(IntEnum(InfoType))
    hiking = Column(Boolean)
    bicycle = Column(Boolean)
    internet_access = Column(UnicodeText)
    stars = Column(Integer)
    map_type = Column(UnicodeText)
    map_size = Column(UnicodeText)
    description = Column(UnicodeText)
    ski = Column(Boolean)
    fireplace = Column(Boolean)
    artist_name = Column(UnicodeText)
    artwork_type = Column(IntEnum(ArtWorkType))
    start_date = Column(UnicodeText)
    smoking = Column(IntEnum(SmokingType))
    phone = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    barrier_type = Column(IntEnum(BarrierType))
    direction = Column(UnicodeText)
    material = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    inscription = Column(UnicodeText)
    foot = Column(Boolean)
    email = Column(UnicodeText)
    zoo = Column(UnicodeText)
    height = Column(Integer)
    man_made = Column(IntEnum(ManMade))
    historic = Column(IntEnum(HistoricType))
    amenity = Column(IntEnum(Amenity))
    building = Column(IntEnum(BuildingType))
    natural = Column(IntEnum(NaturalType))
    cuisine = Column(UnicodeText)
    building_part = Column(IntEnum(BuildingPartType))
    internet_access_fee = Column(Boolean)
    roof_height = Column(Integer)
    roof_shape = Column(IntEnum(RoofShape))
    wikidata = Column(UnicodeText)
    heritage = Column(Integer)
    heritage_operator = Column(UnicodeText)
    fee = Column(Boolean)
    old_name = Column(UnicodeText)
    designation = Column(UnicodeText)
    rooms = Column(Integer)
    image = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    access = Column(IntEnum(AccessType))
    disused = Column(Boolean)
    layer = Column(Integer)
    architect = Column(UnicodeText)
    leisure = Column(IntEnum(LeisureType))
    alt_name = Column(UnicodeText)
    level = Column(Integer)
    loc_name = Column(UnicodeText)
    bitcoin_payment = Column(Boolean)
    noname = Column(Boolean)
    attraction = Column(IntEnum(AttractionType))