import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from . import Building
from .enums import ShopType, LandType

class SecondHandType(enum.Enum):
    none = 0
    only = 1
    yes = 2

class SkiingType(enum.Enum):
    nordic = 0

class Shop(Building):
    __tablename__ = "shops"
    __mapper_args__ = {'polymorphic_identity': 'shop'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    type = Column(Enum(ShopType), nullable=False)
    vehicle_parts = Column(UnicodeText)
    vehicle_repair = Column(UnicodeText)
    organic = Column(Boolean)
    coins_payment = Column(Boolean)
    maestro_payment = Column(Boolean)
    mastercard_payment = Column(Boolean)
    notes_payment = Column(Boolean)
    visa_payment = Column(Boolean)
    bitcoin_payment = Column(Boolean)
    second_hand = Column(Enum(SecondHandType))
    brand = Column(UnicodeText)
    service = Column(UnicodeText)
    skiing = Column(Enum(SkiingType)) # Do we want a skiing_shop?
    landuse = Column(Enum(LandType))
    wine = Column(Boolean)