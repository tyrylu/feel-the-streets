import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import ShopType, OSMObjectType

class SecondHandType(enum.Enum):
    none = 0
    only = 1
    yes = 2
    no = 3

class SkiingType(enum.Enum):
    nordic = 0

class Shop(Building):
    __tablename__ = "shops"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["buildings.id", "buildings.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'shop'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(ShopType))
    vehicle_parts = Column(UnicodeText)
    vehicle_repair = Column(UnicodeText)
    organic = Column(Boolean)
    coins_payment = Column(Boolean)
    second_hand = Column(IntEnum(SecondHandType))
    service = Column(UnicodeText)
    skiing = Column(IntEnum(SkiingType)) # Do we want a skiing_shop?
    wine = Column(Boolean)