import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, Enum
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class AdvertisingType(enum.Enum):
    column = 0
    billboard = 1
    totem = 2
    
    

class Advertising(Entity):
    __tablename__ = "advertisings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'advertising'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(AdvertisingType), nullable=False)
    height = Column(Integer)