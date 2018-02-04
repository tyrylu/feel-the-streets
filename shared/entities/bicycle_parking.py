import enum
from . import Amenity
from .enums import SurveillanceType, SurveillanceKind, SurveillanceZone

class BicycleParkingType(enum.Enum):
    unknown = 0
    stands = 1
    lockers = 2
    ground_slots = 3
    wall_loops = 4
    informal = 5
    anchors = 6
    shed = 7
    wall_hoops = 8
    rack = 9
    
class BicycleParking(Amenity):
    parking_type: BicycleParkingType = None
    surveillance: SurveillanceType = None
    surveillance_type: SurveillanceKind = None
    surveillance_zone: SurveillanceZone = None
    food: bool = None
    real_ale: bool = None
    service_chain_tool: bool = None