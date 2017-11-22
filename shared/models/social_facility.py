import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from . import Amenity
from .enums import BuildingType, OSMObjectType

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
    __tablename__ = "social_facilities"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["amenities.id", "amenities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'social_facility'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    facility_type = Column(IntEnum(SocialFacilityType), nullable=False)
    expected_users = Column(IntEnum(SocialFacilityUser))
    building_type = Column(IntEnum(BuildingType))
    flats = Column(Integer)
    levels = Column(Integer)
    