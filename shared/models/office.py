import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Addressable
from .enums import SmokingType

class OfficeType(enum.Enum):
    yes = -1
    employment_agency = 0
    insurance = 1
    physician = 2
    government = 3
    ngo = 4
    administrative = 5
    company = 6
    tax = 7

class GovernmentRelation(enum.Enum):
    tax = 1
class Office(Addressable):
    __tablename__ = "offices"
    __mapper_args__ = {'polymorphic_identity': 'office'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(Enum(OfficeType), nullable=False)
    phone = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    smoking = Column(Enum(SmokingType))
    official_name = Column(UnicodeText)
    levels = Column(Integer)
    government = Column(Enum(GovernmentRelation))
