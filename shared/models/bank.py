import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import BuildingType, OSMObjectType, InternetAccess, OfficeType

class Bank(Addressable):
    __tablename__ = "banks"
    __mapper_args__ = {'polymorphic_identity': 'bank', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
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
    layer = Column(Integer)
    old_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    contactless_payment = Column(Boolean)
    office = Column(IntEnum(OfficeType))

