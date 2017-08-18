import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from .enums import TourismType, SmokingType, BarrierType, InfoType, ManMade, HistoricType, Amenity, BuildingType, NaturalType, BuildingPartType, RoofShape
from . import Addressable

class ArtWorkType(enum.Enum):
    none = 0
    statue = 1
    sculpture = 2
    
class Tourism(Addressable):
    __tablename__ = "tourisms"
    __mapper_args__ = {'polymorphic_identity': 'tourism'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    type = Column(Enum(TourismType), nullable=False)
    operator = Column(UnicodeText)
    information_type = Column(Enum(InfoType))
    hiking = Column(Boolean)
    bicycle = Column(Boolean)
    internet_access = Column(UnicodeText)
    stars = Column(Integer)
    map_type = Column(UnicodeText)
    map_size = Column(UnicodeText)
    description = Column(UnicodeText)
    ski = Column(Boolean)
    fireplace = Column(Boolean)
    artist_name = Column(UnicodeText)
    artwork_type = Column(Enum(ArtWorkType))
    start_date = Column(UnicodeText)
    smoking = Column(Enum(SmokingType))
    phone = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    barrier_type = Column(Enum(BarrierType))
    direction = Column(UnicodeText)
    material = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    inscription = Column(UnicodeText)
    foot = Column(Boolean)
    email = Column(UnicodeText)
    zoo = Column(UnicodeText)
    height = Column(Integer)
    man_made = Column(Enum(ManMade))
    historic = Column(Enum(HistoricType))
    amenity = Column(Enum(Amenity))
    building = Column(Enum(BuildingType))
    natural = Column(Enum(NaturalType))
    cuisine = Column(UnicodeText)
    building_part = Column(Enum(BuildingPartType))
    internet_access_fee = Column(Boolean)
    roof_height = Column(Integer)
    roof_shape = Column(Enum(RoofShape))
    wikidata = Column(UnicodeText)