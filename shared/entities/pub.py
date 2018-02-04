from .enums import SmokingType,  WheelchairAccess, SportType, WifiType, ShopType, LeisureType
from . import Addressable

class Pub(Addressable):
    phone: str = None
    smoking: SmokingType = None
    facebook: str = None
    brewery: str = None
    flats: int = None
    levels: int = None
    outdoor_seating: bool = None
    start_date: str = None
    wheelchair: WheelchairAccess = None
    cuisine: str = None
    # Make it a list of Cuisine enum members
    wifi: WifiType = None
    sport: SportType = None
    designation: str = None
    takeaway: bool = None
    internet_access_fee: bool = None
    food: bool = None
    url: str = None
    operator: str = None
    other_payment: bool = None
    cash_payment: bool = None
    debitcards_payment: bool = None
    shop: ShopType = None
    phone_1: str = None
    opening_date: str = None
    leisure: LeisureType = None
    litecoin_payment: bool = None
    ethereum_payment: bool = None
    meal_vouchers_payment: bool = None
    gambling: bool = None
    jcb_payment: bool = None
    visa_payment: bool = None
    cryptocurrencies_payment: bool = None
    beer_garden: bool = None