import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import SmokingType, OSMObjectType, LandType, BarrierType, WheelchairAccess

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
    religion = 8
    it = 9
    architect = 10
    estate_agent = 11
    therapist = 12
    telecommunication = 13
    lawyer = 14
    water_utility = 15
    educational_institution = 16
    coworking = 17
    translation = 18
    research = 19
    coworking_space = 20
    travel_agent = 21
    camping = 22
    money_lender = 23
    guide = 24
    financial = 25
    publisher = 26
    print_distribution = 27
    logistics = 28
    reception = 29
    

class GovernmentRelation(enum.Enum):
    tax = 1
    transportation = 2
    cadaster = 3
    ministry = 4
    archive = 5
    
class Office(Addressable):
    __tablename__ = "offices"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["addressables.id", "addressables.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'office'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(OfficeType), nullable=False)
    phone = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    smoking = Column(IntEnum(SmokingType))
    official_name = Column(UnicodeText)
    levels = Column(Integer)
    government = Column(IntEnum(GovernmentRelation))
    landuse = Column(IntEnum(LandType))
    short_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    phone = Column(UnicodeText)
    denomination = Column(UnicodeText)
    religion = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    operator = Column(UnicodeText)
    brand = Column(UnicodeText)
    email = Column(UnicodeText)
    description = Column(UnicodeText)
    bitcoin_payment = Column(Boolean)
    level = Column(Integer)
    