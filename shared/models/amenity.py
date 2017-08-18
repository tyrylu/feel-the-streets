import enum
from sqlalchemy import Column, ForeignKey, Integer, Enum, Boolean, UnicodeText
from . import Addressable
from .enums import Amenity, AccessType, SmokingType, HistoricType, BarrierType


class PlaceType(enum.Enum):
    none = 0
    neighbourhood = 1

class Amenity(Addressable):
    __tablename__ = "amenities"
    __mapper_args__ = {'polymorphic_identity': 'amenity'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(Enum(Amenity))
    religion = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    operator = Column(UnicodeText)
    cuisine = Column(UnicodeText)
    phone = Column(UnicodeText)
    official_name = Column(UnicodeText)
    community_centre_for = Column(UnicodeText)
    takeaway = Column(UnicodeText)
    vending = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    access = Column(Enum(AccessType))
    smoking = Column(Enum(SmokingType))
    amenity_1 = Column(Enum(Amenity))
    drive_through = Column(Boolean)
    backrest = Column(Boolean)
    material = Column(UnicodeText)
    place_type = Column(Enum(PlaceType))
    seats = Column(Integer)
    unisex = Column(Boolean)
    covered = Column(Boolean)
    wheelchair = Column(Boolean)
    facebook = Column(UnicodeText)
    shelter = Column(Boolean)
    hide = Column(Boolean)
    url = Column(UnicodeText)
    denomination = Column(UnicodeText)
    vegetarian_diet = Column(Boolean)
    email = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    historic = Column(Enum(HistoricType))
    dispensing = Column(Boolean)
    barrier = Column(Enum(BarrierType))
    capacity = Column(Integer)
    emergency = Column(Boolean)
    old_name = Column(UnicodeText)
    brewery = Column(UnicodeText)
    delivery = Column(Boolean)
    postal_code = Column(Integer)
    open_air = Column(Boolean)
