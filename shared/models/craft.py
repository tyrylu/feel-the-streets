import enum
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from . import Named
from .enums import BuildingType, LandType, OSMObjectType

class CraftType(enum.Enum):
    carpenter = 0
    photographer = 1
    brewery = 2
    roofer = 3
    shoemaker = 4
    watchmaker = 5
    upholsterer = 6
    confectionery = 7
    dressmaker = 8
    key_cutter = 9
    electrician = 10
    handicraft = 11
    window_construction = 12
    plumber = 13
    tailor = 14
    jeweller = 15
    basket_maker = 16
    glaziery = 17
    photographic_laboratory = 18
    bookbinder = 19
    locksmith = 20
    stonemason = 21
    hvac = 22
    graphic_designer = 23
    designer = 24
    winery = 25
    caterer = 26
    gardener = 27
    
    
class Craft(Named):
    __tablename__ = "crafts"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'craft'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(CraftType), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    operator = Column(UnicodeText)
    building = Column(IntEnum(BuildingType))
    outdoor_seating = Column(Boolean)
    opening_hours = Column(UnicodeText)
    microbrewery = Column(Boolean)
    website = Column(UnicodeText)
    landuse = Column(IntEnum(LandType))
    email = Column(UnicodeText)
    phone = Column(UnicodeText)