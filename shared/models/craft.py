import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from sqlalchemy.orm import relationship
from . import Named
from .enums import BuildingType, LandType

class CraftType(enum.Enum):
    carpenter = 0
    photographer = 1
    brewery = 2
    roofer = 3

class Craft(Named):
    __tablename__ = "crafts"
    __mapper_args__ = {'polymorphic_identity': 'craft'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(CraftType), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    operator = Column(UnicodeText)
    building = Column(Enum(BuildingType))
    outdoor_seating = Column(Boolean)
    opening_hours = Column(UnicodeText)
    microbrewery = Column(Boolean)
    website = Column(UnicodeText)
    landuse = Column(Enum(LandType))
    email = Column(UnicodeText)
    phone = Column(UnicodeText)