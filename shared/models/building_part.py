import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Entity
from .enums import BuildingPartType

class RoofShape(enum.Enum):
    gabled =  0
    
class RoofOrientation(enum.Enum):
    across = 0

class BuildingPart(Entity):
    __tablename__ = "building_parts"
    __mapper_args__ = {'polymorphic_identity': 'building_part'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(BuildingPartType))
    roof_shape = Column(Enum(RoofShape))
    roof_orientation = Column(Enum(RoofOrientation))