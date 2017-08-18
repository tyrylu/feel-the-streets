import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity

class DisusedType(enum.Enum):
    quarry = 0

class Disused(Entity):
    __tablename__ = "disused"
    __mapper_args__ = {'polymorphic_identity': 'disused'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(DisusedType), nullable=False)