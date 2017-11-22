import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import ManMade
from .enums import BuildingPartType, OSMObjectType, BuildingType, TourismType

class TowerType(enum.Enum):
    unknown  = 0
    communication = 1
    observation = 2
    climbing = 3
    bell_tower = 4
    bts = 5
    lighting = 6
    church = 7
    cooling = 8

    
    

class Tower(ManMade):
    __tablename__ = "towers"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["man_made.id", "man_made.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'tower'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    tower_type = Column(IntEnum(TowerType))
    building_part = Column(IntEnum(BuildingPartType))
    building = Column(IntEnum(BuildingType))
    note = Column(UnicodeText)
    tourism = Column(IntEnum(TourismType))
    fee = Column(Boolean)
    mobile_phone_communication  = Column(Boolean)
    tower_construction = Column(UnicodeText)