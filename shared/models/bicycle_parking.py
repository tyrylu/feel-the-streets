import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Amenity

class BicycleParkingType(enum.Enum):
    unknown = 0
    stands = 1
    lockers = 2
    ground_slots = 3

class BicycleParking(Amenity):
    __tablename__ = "bicycle_parkings"
    __mapper_args__ = {'polymorphic_identity': 'bicycle_parking'}
    id = Column(Integer, ForeignKey("amenities.id"), primary_key=True)
    parking_type = Column(Enum(BicycleParkingType))
