import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from sqlalchemy.orm import relationship
from .enums import AccessType, BuildingType
from . import Named

class ParkingType(enum.Enum):
    unspecified = 0
    surface = 1
    multi_storey = 2
    underground = 3
    rooftop = 4

class Parking(Named):
    __tablename__ = "parkings"
    __mapper_args__ = {'polymorphic_identity': 'parking'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    paid = Column(UnicodeText)
    capacity = Column(Integer)
    capacity_for_disabled = Column(UnicodeText) # Someone treats it as a bool, someone as an int.
    operator = Column(UnicodeText)
    access = Column(Enum(AccessType))
    type = Column(Enum(ParkingType))
    supervised = Column(Boolean)
    designation = Column(UnicodeText)
    building_type = Column(Enum(BuildingType))
    surface = Column(UnicodeText)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    park_ride = Column(Boolean)
    layer = Column(Integer)
    website = Column(UnicodeText)