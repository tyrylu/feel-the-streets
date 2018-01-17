import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import ManMade, TourismType, NaturalType, OSMObjectType, LandType, BarrierType, FenceType, GolfRelation, GardenType, SportType, HistoricType
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
    __tablename__ = "naturals"
    __mapper_args__ = {'polymorphic_identity': 'natural', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(NaturalType), nullable=False)
    lining = Column(UnicodeText)
    man_made = Column(IntEnum(ManMade))
    depth = Column(Float)
    ele = Column(Float)
    note = Column(UnicodeText)
    drinking_water = Column(Boolean)
    alt_name = Column(UnicodeText)
    website = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    inscription = Column(UnicodeText)
    tourism_type = Column(IntEnum(TourismType))
    opening_hours = Column(UnicodeText)
    surface = Column(UnicodeText)
    material = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    barrier = Column(IntEnum(BarrierType))
    fence_type = Column(IntEnum(FenceType))
    leaf_type = Column(UnicodeText)
    # Map them correctly to a tree
    golf = Column(IntEnum(GolfRelation))
    natural_1 = Column(IntEnum(NaturalType))
    description = Column(UnicodeText)
    layer = Column(Integer)
    uhul_area = Column(UnicodeText)
    height = Column(Float)
    uhul_slt = Column(UnicodeText)
    garden_type = Column(IntEnum(GardenType))
    fixme = Column(UnicodeText)
    sport = Column(IntEnum(SportType))
    landcover = Column(UnicodeText)
    historic = Column(IntEnum(HistoricType))
    is_in = Column(UnicodeText)
    wetland = Column(IntEnum(WetLandType))
    leaf_cycle = Column(IntEnum(LeafCycle))
    url = Column(UnicodeText)
    import_ref = Column(UnicodeText)
    wood = Column(IntEnum(LeafCycle))

