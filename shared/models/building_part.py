import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from . import Entity
from .enums import BuildingPartType, RoofShape, OSMObjectType

class RoofOrientation(enum.Enum):
    across = 0
    along = 1
    
class BuildingPart(Entity):
    __tablename__ = "building_parts"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'building_part'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(BuildingPartType))
    roof_shape = Column(IntEnum(RoofShape))
    roof_orientation = Column(IntEnum(RoofOrientation))