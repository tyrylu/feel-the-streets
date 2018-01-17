import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import ManMade
from .enums import BuildingPartType, OSMObjectType, BuildingType, TourismType, RoofShape, TowerType

class Tower(ManMade):
    __tablename__ = "towers"
    __mapper_args__ = {'polymorphic_identity': 'tower', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("man_made.id"), primary_key=True)
    tower_type = Column(IntEnum(TowerType))
    building_part = Column(IntEnum(BuildingPartType))
    building = Column(IntEnum(BuildingType))
    tourism = Column(IntEnum(TourismType))
    fee = Column(Boolean)
    mobile_phone_communication  = Column(Boolean)
    tower_construction = Column(UnicodeText)
    colour = Column(UnicodeText)
    roof_shape = Column(IntEnum(RoofShape))
    levels = Column(Integer)
    alt_name = Column(UnicodeText)
    min_height = Column(Integer)
    roof_colour = Column(UnicodeText)
    phone = Column(UnicodeText)
    ele = Column(Integer)
    opening_hours = Column(UnicodeText)
    flats = Column(Integer)
    microwave_communication = Column(Boolean)
    television_communication = Column(Boolean)
    communication = Column(UnicodeText)
