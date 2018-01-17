from sqlalchemy import Column, ForeignKey, Integer, Boolean, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import OSMObjectType, WheelchairAccess, Location, AccessType

class ATM(Addressable):
    __tablename__ = "atms"
    __mapper_args__ = {'polymorphic_identity': 'atm', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    operator = Column(UnicodeText)
    contact_website = Column(UnicodeText)
    fee = Column(UnicodeText)
    drive_through = Column(Boolean)
    phone = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    brand = Column(UnicodeText)
    layer = Column(Integer)
    location = Column(IntEnum(Location))
    cash_in = Column(Boolean)
    bitcoin = Column(Boolean)
    access = Column(IntEnum(AccessType))

