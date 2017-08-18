import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity

class ConstructionType(enum.Enum):
    railway = 0

class Construction(Entity):
    __tablename__ = "constructions"
    __mapper_args__ = {'polymorphic_identity': 'construction'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(ConstructionType), nullable=False)