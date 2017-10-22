import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class RecyclingType(enum.Enum):
    unknown = 0
    centre = 1
    container = 2
    underground = 3

class Recycling(Named):
    __tablename__ = "recyclings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'recycling'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(RecyclingType))
    telephone = Column(UnicodeText)
    website = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    glass = Column(Boolean)
    glass_bottles = Column(Boolean)
    plastic_bottles = Column(Boolean)
    plastic_packaging = Column(Boolean)
    clothes = Column(Boolean)
    paper = Column(Boolean)
    plastic = Column(Boolean)
    electrical_appliances = Column(Boolean)
    batteries = Column(Boolean)
    cartons = Column(Boolean)
    beverage_cartons = Column(Boolean)
    small_appliances = Column(Boolean)
    cans = Column(Boolean)
    pet = Column(Boolean)
    electrical_items = Column(Boolean)
    furniture = Column(Boolean)
    hazardous_waste = Column(Boolean)
    tyres = Column(Boolean)
    organic = Column(Boolean)