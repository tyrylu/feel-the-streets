import enum
from sqlalchemy import Column, ForeignKey, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import HistoricType, OSMObjectType, MemorialType, Direction, SiteType, Material, Role, ArtWorkType

class TombType(enum.Enum):
    tombstone = 0
    vault = 1
    war_grave = 2

class Historic(Named):
    __tablename__ = "historic"
    __mapper_args__ = {'polymorphic_identity': 'historic', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(HistoricType), nullable=False)
    ele = Column(Float)
    inscription = Column(UnicodeText)
    religion = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    denomination = Column(UnicodeText)
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    ruins = Column(Boolean)
    wikidata = Column(UnicodeText)
    heritage = Column(Integer)
    heritage_operator = Column(UnicodeText)
    wikimedia_commons = Column(UnicodeText)
    image = Column(UnicodeText)
    description = Column(UnicodeText)
    memorial_type = Column(IntEnum(MemorialType))
    memorial_name = Column(UnicodeText)
    note = Column(UnicodeText)
    artist_name = Column(UnicodeText)
    wheelchair = Column(Boolean)
    direction = Column(IntEnum(Direction))
    tomb = Column(IntEnum(TombType))
    end_date = Column(Integer)
    site_type = Column(IntEnum(SiteType))
    material = Column(IntEnum(Material))
    date = Column(UnicodeText)
    height = Column(Integer)
    monument = Column(IntEnum(Role))
    addr = Column(UnicodeText)
    person_date_of_birth = Column(UnicodeText)
    artwork_type = Column(IntEnum(ArtWorkType))

