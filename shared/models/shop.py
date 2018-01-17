import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import ShopType, OSMObjectType

class SecondHandType(enum.Enum):
    none = 0
    only = 1
    yes = 2
    no = 3

class SkiingType(enum.Enum):
    nordic = 0

class TicketType(enum.Enum):
    public_transport = 0

class TradeType(enum.Enum):
    plumbing = 0
    building_supplies = 1

class BeautyType(enum.Enum):
    tanning = 0
    nails = 1

class HobbyType(enum.Enum):
    rc_models = 0
    models = 1

class Shop(Building):
    __tablename__ = "shops"
    __mapper_args__ = {'polymorphic_identity': 'shop', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    type = Column(IntEnum(ShopType))
    vehicle_parts = Column(UnicodeText)
    vehicle_repair = Column(UnicodeText)
    organic = Column(Boolean)
    coins_payment = Column(Boolean)
    second_hand = Column(IntEnum(SecondHandType))
    service = Column(UnicodeText)
    skiing = Column(IntEnum(SkiingType))
     # Do we want a skiing_shop?
    wine = Column(Boolean)
    tickets = Column(IntEnum(TicketType))
    trade = Column(IntEnum(TradeType))
    beauty = Column(IntEnum(BeautyType))
    hobby = Column(IntEnum(HobbyType))
    jcb_payment = Column(Boolean)
