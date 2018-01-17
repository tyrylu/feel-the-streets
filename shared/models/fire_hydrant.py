import enum
from sqlalchemy import Column, ForeignKey, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class FireHydrantType(enum.Enum):
    unknown = 0
    pillar = 1
    wall = 2
    underground = 3

class FireHydrantPosition(enum.Enum):
    sidewalk = 0
    green = 1
    street = 2

class FireHydrant(Entity):
    __tablename__ = "fire_hydrants"
    __mapper_args__ = {'polymorphic_identity': 'fire_hydrant', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(FireHydrantType), nullable=False)
    position = Column(IntEnum(FireHydrantPosition))
    count = Column(Integer)
