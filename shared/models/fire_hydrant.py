import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity

class FireHydrantType(enum.Enum):
    unknown = 0
    pillar = 1

class FireHydrant(Entity):
    __tablename__ = "fire_hydrants"
    __mapper_args__ = {'polymorphic_identity': 'fire_hydrant'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(FireHydrantType), nullable=False)