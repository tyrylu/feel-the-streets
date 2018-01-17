import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Addressable
from .enums import SmokingType, OSMObjectType, LandType, BarrierType, WheelchairAccess, RoofShape, RoofMaterial, IndoorType, Amenity, InternetAccess, OfficeType

class Function(enum.Enum):
    retail = 0
    headquarters = 1

class AuthorityType(enum.Enum):
    finance = 0
    culture = 1
    interior = 2
    yes = 3

class GovernmentRelation(enum.Enum):
    tax = 1
    transportation = 2
    cadaster = 3
    ministry = 4
    archive = 5
    
class LawyerType(enum.Enum):
    notary = 0

class Office(Addressable):
    __tablename__ = "offices"
    __mapper_args__ = {'polymorphic_identity': 'office', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(IntEnum(OfficeType), nullable=False)
    phone = Column(UnicodeText)
    smoking = Column(IntEnum(SmokingType))
    official_name = Column(UnicodeText)
    levels = Column(Integer)
    government = Column(IntEnum(GovernmentRelation))
    landuse = Column(IntEnum(LandType))
    short_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    phone = Column(UnicodeText)
    denomination = Column(UnicodeText)
    religion = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    operator = Column(UnicodeText)
    brand = Column(UnicodeText)
    bitcoin_payment = Column(Boolean)
    authority = Column(IntEnum(AuthorityType))
    old_name = Column(UnicodeText)
    roof_material = Column(IntEnum(RoofMaterial))
    roof_shape = Column(IntEnum(RoofShape))
    roof_height = Column(Integer)
    roof_colour = Column(UnicodeText)
    flats = Column(Integer)
    function = Column(IntEnum(Function))
    indoor = Column(IntEnum(IndoorType))
    amenity = Column(IntEnum(Amenity))
    fax = Column(UnicodeText)
    lawyer = Column(IntEnum(LawyerType))
    phone_1 = Column(UnicodeText)
    facebook = Column(UnicodeText)
    start_date = Column(UnicodeText)
    designation = Column(UnicodeText)
    description_en = Column(UnicodeText)

