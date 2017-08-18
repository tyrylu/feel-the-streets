from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from .enums import SmokingType
from . import Addressable

class Pub(Addressable):
    __tablename__ = "pubs"
    __mapper_args__ = {'polymorphic_identity': 'pub'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    phone = Column(UnicodeText)
    email = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    smoking = Column(Enum(SmokingType))
    facebook = Column(UnicodeText)
    brewery = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    flats = Column(Integer)
    levels = Column(Integer)