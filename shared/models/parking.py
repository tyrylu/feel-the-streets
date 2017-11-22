import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import AccessType, BuildingType, OSMObjectType, WheelchairAccess, BarrierType, ParkingType, ConstructionType, LandType
from . import Named

class Parking(Named):
    __tablename__ = "parkings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'parking'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    paid = Column(UnicodeText)
    capacity = Column(Integer)
    capacity_for_disabled = Column(UnicodeText) # Someone treats it as a bool, someone as an int.
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