import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Leisure
from .enums import OSMObjectType, GardenType, LandType

class Garden(Leisure):
    __tablename__ = "gardens"
    __mapper_args__ = {'polymorphic_identity': 'garden', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("leisures.id"), primary_key=True)
    garden_type = Column(IntEnum(GardenType))
    landuse = Column(IntEnum(LandType))
    bicycle = Column(Boolean)
    smoking = Column(Boolean)
    official_name = Column(UnicodeText)
