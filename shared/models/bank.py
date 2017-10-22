import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import BuildingType, OSMObjectType

class Bank(Addressable):
    __tablename__ = "banks"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'bank'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    opening_hours = Column(UnicodeText)
    brand = Column(UnicodeText)
    operator = Column(UnicodeText)
    atm = Column(Boolean)
    wheelchair = Column(Boolean)
    drive_through = Column(Boolean)
    phone = Column(UnicodeText)
    flats = Column(Integer)
    levels = Column(Integer)
    building_type = Column(IntEnum(BuildingType))
    start_date = Column(UnicodeText)