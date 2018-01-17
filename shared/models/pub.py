from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import SmokingType, OSMObjectType, WheelchairAccess, SportType, WifiType, ShopType, LeisureType
from . import Addressable

class Pub(Addressable):
    __tablename__ = "pubs"
    __mapper_args__ = {'polymorphic_identity': 'pub', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    phone = Column(UnicodeText)
    smoking = Column(IntEnum(SmokingType))
    facebook = Column(UnicodeText)
    brewery = Column(UnicodeText)
    flats = Column(Integer)
    levels = Column(Integer)
    outdoor_seating = Column(Boolean)
    start_date = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    cuisine = Column(UnicodeText)
    # Make it a list of Cuisine enum members
    wifi = Column(IntEnum(WifiType))
    sport = Column(IntEnum(SportType))
    designation = Column(UnicodeText)
    takeaway = Column(Boolean)
    internet_access_fee = Column(Boolean)
    food = Column(Boolean)
    url = Column(UnicodeText)
    operator = Column(UnicodeText)
    other_payment = Column(Boolean)
    cash_payment = Column(Boolean)
    debitcards_payment = Column(Boolean)
    shop = Column(IntEnum(ShopType))
    phone_1 = Column(UnicodeText)
    opening_date = Column(UnicodeText)
    leisure = Column(IntEnum(LeisureType))
    litecoin_payment = Column(Boolean)
    ethereum_payment = Column(Boolean)
    meal_vouchers_payment = Column(Boolean)
    gambling = Column(Boolean)
    jcb_payment = Column(Boolean)
    visa_payment = Column(Boolean)
    cryptocurrencies_payment = Column(Boolean)
    beer_garden = Column(Boolean)
