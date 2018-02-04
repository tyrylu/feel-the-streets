import enum
from . import Amenity
from .enums import BuildingType

class SocialFacilityType(enum.Enum):
    group_home = 0
    assisted_living = 1
    shelter = 2
    outreach = 3
    advice = 4
    
class SocialFacilityUser(enum.Enum):
    unspecified = 0
    senior = 1
    diseased = 2
    mental_health = 3
    disabled = 4
    homeless = 5
    youth = 6
    
class SocialFacility(Amenity):
    facility_type: SocialFacilityType
    expected_users: SocialFacilityUser = None
    building_type: BuildingType = None
    flats: int = None
    levels: int = None
