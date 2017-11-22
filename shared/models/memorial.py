import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Historic
from .enums import OSMObjectType, WheelchairAccess

class MemorialType(enum.Enum):
    unknown = 0
    plaque = 1
    stolperstein = 2
    statue = 3
    plate = 4
    war_memorial = 5
    
    
class MemorialKind(enum.Enum):
    unknown = 0
    war_memorial = 1
    plaque = 2
    statue = 3
    bust = 4
    stele = 5
    tablet = 6
    stone = 7
    artwork = 8
    
    
class Memorial(Historic):
    __tablename__ = "memorials"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["historic.id", "historic.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'memorial'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    memorial_type = Column(IntEnum(MemorialType))
    memorial_kind = Column(IntEnum(MemorialKind))
    url = Column(UnicodeText)
    artist_name = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    artwork_type = Column(IntEnum(MemorialKind))
    direction = Column(UnicodeText)
    addr = Column(UnicodeText)
    text = Column(UnicodeText)
    network = Column(UnicodeText)
    person_date_of_birth = Column(UnicodeText) # Make it a date in a later pass
    person_date_of_death = Column(UnicodeText)