from . import Named
from .enums import BuildingType, TourismType, InternetAccess, ShelterType

class Shelter(Named):
    type: ShelterType = None
    building: BuildingType = None
    tourism: TourismType = None
    bench: str = None
    internet_access: InternetAccess = None
    internet_access_ssid: str = None
    height: int = None
    description: str = None
    architect: str = None
    fireplace: bool = None
    bin: bool = None