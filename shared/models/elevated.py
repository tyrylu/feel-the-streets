from sqlalchemy import Column, ForeignKey, Boolean, Integer, Float
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Elevated(Entity):
    __tablename__ = "elevated"
    __mapper_args__ = {'polymorphic_identity': 'elevated', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    ele = Column(Float)
    mountain_pass = Column(Boolean)
