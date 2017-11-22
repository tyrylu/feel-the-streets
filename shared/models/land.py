import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import ShopType, ManMade, BarrierType, NaturalType, LeisureType, LandType, OSMObjectType, ConstructionType, IndustrialType, Surface, FenceType
from . import Named

class MeadowType(enum.Enum):
    none = 0
    agricultural = 1
    pasture = 2
    perpetual = 3

class MilitaryType(enum.Enum):
    none = 0
    barracks = 1
    danger_area = 2
class LandCover(enum.Enum):
    grass = 0

class BasinType(enum.Enum):
    detention = 0

class PlantType(enum.Enum):
    tree = 0
class ResidentialType(enum.Enum):
    urban = 0
    
class Land(Named):
    __tablename__ = "lands"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'land'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(LandType), nullable=False)
    shop_type = Column(IntEnum(ShopType))
    website = Column(UnicodeText)
    meadow_type = Column(IntEnum(MeadowType))
    man_made = Column(IntEnum(ManMade))
    crop = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    note = Column(UnicodeText)
    comment = Column(UnicodeText)
    natural_type = Column(IntEnum(NaturalType))
    military_type = Column(IntEnum(MilitaryType))
    operator = Column(UnicodeText)
    resource = Column(UnicodeText)
    leisure = Column(IntEnum(LeisureType))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    leaf_cycle = Column(UnicodeText)
    religion = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    landcover = Column(IntEnum(LandCover))
    description = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    disused = Column(Boolean)
    abandoned = Column(Boolean)
    layer = Column(Integer)
    construction = Column(IntEnum(ConstructionType))
    old_name = Column(UnicodeText)
    industrial = Column(IntEnum(IndustrialType))
    basin = Column(IntEnum(BasinType)) # Separate entity?
    alt_name = Column(UnicodeText)
    fence_type = Column(IntEnum(FenceType))
    fixme = Column(UnicodeText)
    loc_name = Column(UnicodeText)
    residential = Column(IntEnum(ResidentialType))
    surface = Column(IntEnum(Surface))
    plant = Column(IntEnum(PlantType))
