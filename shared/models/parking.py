import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import AccessType, BuildingType, OSMObjectType, WheelchairAccess, BarrierType, ParkingType, ConstructionType, LandType, GardenType
from . import Named

class Smoothness(enum.Enum):
    excellent = 0
    intermediate = 1
    good = 2

class Parking(Named):
    __tablename__ = "parkings"
    __mapper_args__ = {'polymorphic_identity': 'parking', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    paid = Column(UnicodeText)
    capacity = Column(Integer)
    capacity_for_disabled = Column(UnicodeText)
     # Someone treats it as a bool, someone as an int.
    operator = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    type = Column(IntEnum(ParkingType))
    supervised = Column(Boolean)
    designation = Column(UnicodeText)
    building_type = Column(IntEnum(BuildingType))
    surface = Column(UnicodeText)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    park_ride = Column(Boolean)
    layer = Column(Integer)
    website = Column(UnicodeText)
    building_levels = Column(Integer)
    opening_hours = Column(UnicodeText)
    start_date = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    barrier = Column(IntEnum(BarrierType))
    capacity_for_parents = Column(Boolean)
    capacity_for_women = Column(Boolean)
    lit = Column(Boolean)
    description = Column(UnicodeText)
    fixme = Column(UnicodeText)
    covered = Column(Boolean)
    construction = Column(IntEnum(ConstructionType))
    landuse = Column(IntEnum(LandType))
    maxstay = Column(UnicodeText)
    maxheight = Column(Float)
    smoothness = Column(IntEnum(Smoothness))
    fenced = Column(Boolean)
    level = Column(UnicodeText)
    email = Column(UnicodeText)
    bus = Column(Boolean)
    garden_type = Column(IntEnum(GardenType))
    foot = Column(Boolean)
    height = Column(UnicodeText)
    demolished_building = Column(IntEnum(BuildingType))
    bicycle = Column(Boolean)
    motorcycle = Column(Boolean)
    old_name = Column(UnicodeText)
