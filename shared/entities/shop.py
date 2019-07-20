import enum
from shared.humanization_utils import underscored_to_words
from . import Building
from .enums import ShopType

class ShopItemAvailability(enum.Enum):
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
    type: ShopType = None
    vehicle_parts: str = None
    vehicle_repair: str = None
    organic: ShopItemAvailability = None
    coins_payment: bool = None
    second_hand: ShopItemAvailability = None
    service: str = None
    skiing: SkiingType = None
     # Do we want a skiing_shop?
    wine: bool = None
    tickets: TicketType = None
    trade: TradeType = None
    beauty: BeautyType = None
    hobby: HobbyType = None
    jcb_payment: bool = None

    def __str__(self):
        retval = super().__str__()
        if self.type:
            retval += " ({})".format(underscored_to_words(self.type.name))
        return retval