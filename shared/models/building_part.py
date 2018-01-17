import enum
from sqlalchemy import Column, ForeignKey, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Entity
from .enums import BuildingPartType, RoofShape, OSMObjectType, RoofOrientation, RoofMaterial, Material

class BuildingPart(Entity):
    __tablename__ = "building_parts"
    __mapper_args__ = {'polymorphic_identity': 'building_part', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(BuildingPartType))
    roof_shape = Column(IntEnum(RoofShape))
    roof_orientation = Column(IntEnum(RoofOrientation))
    levels = Column(Integer)
    height = Column(Integer)
    roof_direction = Column(Integer)
    roof_height = Column(Integer)
    roof_material = Column(IntEnum(RoofMaterial))
    roof_colour = Column(UnicodeText)
    roof_slope_direction = Column(Float)
    building_material = Column(IntEnum(Material))
    level = Column(UnicodeText)
    material = Column(IntEnum(Material))
    fixme = Column(UnicodeText)
