from . import OSMEntity
from .enums import BuildingPartType, RoofShape, RoofOrientation, RoofMaterial, Material

class BuildingPart(OSMEntity):
    type: BuildingPartType = None
    roof_shape: RoofShape = None
    roof_orientation: RoofOrientation = None
    levels: int = None
    height: int = None
    roof_direction: int = None
    roof_height: int = None
    roof_material: RoofMaterial = None
    roof_colour: str = None
    roof_slope_direction: float = None
    building_material: Material = None
    level: str = None
    material: Material = None
    fixme: str = None