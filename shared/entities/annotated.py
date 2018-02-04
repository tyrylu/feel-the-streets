from . import Named
from .enums import AccessType, RouteType, BuildingType, ConstructionType, RoofShape, RailWayType

class Annotated(Named):
    note: str = None
    fixme: str = None
    website: str = None
    level: int = None
    removed_name: str = None
    building_part: bool = None
    access: AccessType = None
    complete: bool = None
    route_master: RouteType = None
    lock: bool = None
    historic_building: BuildingType = None
    proposed: ConstructionType = None
    building_colour: str = None
    roof_shape: RoofShape = None
    disused_railway: RailWayType = None
    phone: str = None
    removed_phone: str = None