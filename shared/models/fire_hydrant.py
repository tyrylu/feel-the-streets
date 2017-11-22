import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class FireHydrantType(enum.Enum):
    unknown = 0
    pillar = 1
    wall = 2
    
class FireHydrantPosition(enum.Enum):
    sidewalk = 0
    green = 1

class FireHydrant(Entity):
    __tablename__ = "fire_hydrants"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'fire_hydrant'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(FireHydrantType), nullable=False)
    position = Column(IntEnum(FireHydrantPosition))