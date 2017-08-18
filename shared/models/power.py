import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity

class PowerType(enum.Enum):
    tower = 0
    substation = 1
    portal = 2
    station = 3

class Power(Entity):
    __tablename__ = "powers"
    __mapper_args__ = {'polymorphic_identity': 'power'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(PowerType), nullable=False)