import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .enums import SportType
from . import Named

class SwimmingType(enum.Enum):
    none = 0
    natural = 1

class Sport(Named):
    __tablename__ = "sports"
    __mapper_args__ = {'polymorphic_identity': 'sport'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(SportType), nullable=False)
    swimming = Column(Enum(SwimmingType))