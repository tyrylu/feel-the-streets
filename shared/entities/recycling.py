import enum
from . import Named
from .enums import BarrierType, FenceType, Location

class RecyclingType(enum.Enum):
    unknown = 0
    centre = 1
    container = 2
    underground = 3

class Recycling(Named):
    type: RecyclingType = None
    phone: str = None
    website: str = None
    opening_hours: str = None
    glass: bool = None
    glass_bottles: bool = None
    plastic_bottles: bool = None
    plastic_packaging: bool = None
    clothes: bool = None
    paper: bool = None
    plastic: bool = None
    electrical_appliances: bool = None
    batteries: bool = None
    cartons: bool = None
    beverage_cartons: bool = None
    small_appliances: bool = None
    cans: bool = None
    pet: bool = None
    electrical_items: bool = None
    furniture: bool = None
    hazardous_waste: bool = None
    tyres: bool = None
    organic: bool = None
    barrier: BarrierType = None
    scrap_metal: bool = None
    fence_type: FenceType = None
    operator: str = None
    waste: bool = None
    cardboard: bool = None
    magazines: bool = None
    newspaper: bool = None
    paper_packaging: bool = None
    location: Location = None
    books: bool = None
    green_waste: bool = None
    wood: bool = None
    glass_green: bool = None
    glass_white: bool = None
    shoes: bool = None
    drinking_cartons: bool = None
    mobile_phones: bool = None
    plastic_bags: bool = None
    electronics: bool = None
    designation: str = None
    email: str = None
    underground: bool = None
    # Make the specific recycable things a flags field.