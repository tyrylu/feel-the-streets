from . import Road
from .enums import Amenity, OSMObjectType, AccessType, ParkingType

class ServiceRoad(Road):
    delivery: bool = None
    frequency: int = None
    vehicle_backward: AccessType = None
    parking: ParkingType = None
    todo: str = None