from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import HistoricType, OSMObjectType, LandType, BarrierType, NaturalType, Material, ArtWorkType, TourismType
from . import Named

class Fountain(Named):
    __tablename__ = "fountains"
    __mapper_args__ = {'polymorphic_identity': 'fountain', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    drinking_water = Column(Boolean)
    historic = Column(IntEnum(HistoricType))
    old_name = Column(UnicodeText)
    loc_name = Column(UnicodeText)
    note = Column(UnicodeText)
    architect = Column(UnicodeText)
    lit = Column(Boolean)
    landuse = Column(IntEnum(LandType))
    wikipedia = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    layer = Column(Integer)
    artist_name = Column(UnicodeText)
    alt_name = Column(UnicodeText)
    sorting_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    natural = Column(IntEnum(NaturalType))
    material = Column(IntEnum(Material))
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    artwork_type = Column(IntEnum(ArtWorkType))
    width = Column(Float)
    disused = Column(Boolean)
    fixme = Column(UnicodeText)
    tourism = Column(IntEnum(TourismType))
