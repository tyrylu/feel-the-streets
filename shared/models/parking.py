import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import AccessType, BuildingType, OSMObjectType
from . import Named

class ParkingType(enum.Enum):
    unspecified = 0
    surface = 1
    multi_storey = 2
    underground = 3
    rooftop = 4
    asphalt = 5
    lane = 6
    kiss_and_ride = 7
    garage = 8
    carports = 9
    
    
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