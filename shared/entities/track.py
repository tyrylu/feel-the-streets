from . import Road
from .enums import Inclination, LeisureType, AccessType, BuildingType, RouteImportance

class Track(Road):
    motorcar_allowed: AccessType = None
    leisure: LeisureType = None
    mtb_scale: int = None
    mtb_scale_uphill: int = None
    forestry: bool = None
    bicycle_class: int = None
    ticks_description: str = None
    motor_vehicle_note: str = None
    proposed_segregated: bool = None
    steep_incline: bool = None
    trasa: int = None
    sprint_lanes: int = None
    todo: str = None
    kct_barva: RouteImportance = None
    designation: str = None
