import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer
from . import Amenity

class SocialFacilityType(enum.Enum):
    group_home = 0
    assisted_living = 1

class SocialFacilityUser(enum.Enum):
    unspecified = 0
    senior = 1

class SocialFacility(Amenity):
    __tablename__ = "social_facilities"
    __mapper_args__ = {'polymorphic_identity': 'social_facility'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    facility_type = Column(Enum(SocialFacilityType), nullable=False)
    expected_users = Column(Enum(SocialFacilityUser))