import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Leisure

class GardenType(enum.Enum):
    residential = 0

class Garden(Leisure):
    __tablename__ = "gardens"
    __mapper_args__ = {'polymorphic_identity': 'garden'}
    id = Column(Integer, ForeignKey("leisures.id"), primary_key=True)
    garden_type = Column(Enum(GardenType))