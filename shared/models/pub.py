from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import SmokingType, OSMObjectType, WheelchairAccess, SportType, WifiType
from . import Addressable

class Pub(Addressable):
    __tablename__ = "pubs"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'pub'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    phone = Column(UnicodeText)
    email = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    smoking = Column(IntEnum(SmokingType))
    facebook = Column(UnicodeText)
    brewery = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    flats = Column(Integer)
    levels = Column(Integer)
    loc_name = Column(UnicodeText)
    outdoor_seating = Column(Boolean)
    start_date = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    cuisine = Column(UnicodeText) # Make it a list of Cuisine enum members
    wifi = Column(IntEnum(WifiType))
    sport = Column(IntEnum(SportType))
    designation = Column(UnicodeText)
    takeaway = Column(Boolean)
    