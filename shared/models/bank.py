import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText

from . import Addressable
from .enums import BuildingType



class Bank(Addressable):
    __tablename__ = "banks"
    __mapper_args__ = {'polymorphic_identity': 'bank'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    opening_hours = Column(UnicodeText)
    brand = Column(UnicodeText)
    operator = Column(UnicodeText)
    atm = Column(Boolean)
    wheelchair = Column(Boolean)
    drive_through = Column(Boolean)
    phone = Column(UnicodeText)
    flats = Column(Integer)
    levels = Column(Integer)
    building_type = Column(Enum(BuildingType))
    start_date = Column(UnicodeText)