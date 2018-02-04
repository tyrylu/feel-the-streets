import enum
from . import Named, Address
from .enums import InternetAccess

class ClubType(enum.Enum):
    yes = 1
    scuba_diving = 2
    music = 3
    board_games = 4
    

class Addressable(Named):
    address: Address = None
    note: str = None
    is_in: str = None
    fixme: str = None
    website: str = None
    ele: float = None
    club: ClubType = None
    description: str = None
    level: int = None
    email: str = None
    wikidata: str = None
    alt_name: str = None
    loc_name: str = None
    comment: str = None
    opening_hours: str = None
    disused_name: str = None
    internet_access: InternetAccess = None

    def __str__(self):
        return super().__str__() + (", " + str(self.address) if self.address else "")