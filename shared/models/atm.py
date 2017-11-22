from sqlalchemy import Column, ForeignKeyConstraint, Integer, Boolean, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import OSMObjectType, WheelchairAccess

class ATM(Addressable):
    __tablename__ = "atms"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'atm'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    operator = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    contact_website = Column(UnicodeText)
    fee = Column(UnicodeText)
    description = Column(UnicodeText)
    drive_through = Column(Boolean)
    phone = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    level = Column(Integer)
    brand = Column(UnicodeText)
    