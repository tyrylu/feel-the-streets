import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import ManMade
from .enums import BuildingPartType

class TowerType(enum.Enum):
    unknown  = 0
    communication = 1
    observation = 2

class Tower(ManMade):
    __tablename__ = "towers"
    __mapper_args__ = {'polymorphic_identity': 'tower'}
    id = Column(Integer, ForeignKey("man_made.id"), primary_key=True)
    tower_type = Column(Enum(TowerType))
    building_part = Column(Enum(BuildingPartType))