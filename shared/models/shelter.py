import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import BuildingType, OSMObjectType, TourismType, InternetAccess, ShelterType

class Shelter(Entity):
    __tablename__ = "shelters"
    __mapper_args__ = {'polymorphic_identity': 'shelter', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(ShelterType))
    building = Column(IntEnum(BuildingType))
    tourism = Column(IntEnum(TourismType))
    bench = Column(UnicodeText)
    name = Column(UnicodeText)
    internet_access = Column(IntEnum(InternetAccess))
    internet_access_ssid = Column(UnicodeText)
    height = Column(Integer)
    description = Column(UnicodeText)
    architect = Column(UnicodeText)
    fireplace = Column(Boolean)
    bin = Column(Boolean)
