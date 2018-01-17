import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType, Amenity, RoadType

class DisusedType(enum.Enum):
    quarry = 0
    yes = 1

class Disused(Entity):
    __tablename__ = "disused"
    __mapper_args__ = {'polymorphic_identity': 'disused', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(DisusedType), nullable=False)
    denomination = Column(UnicodeText)
    destroyed_amenity = Column(IntEnum(Amenity))
    destroyed_name = Column(UnicodeText)
    end_date = Column(UnicodeText)
    start_date = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    religion = Column(UnicodeText)
    highway = Column(IntEnum(RoadType))
    operator = Column(UnicodeText)
    foot = Column(Boolean)
    name = Column(UnicodeText)
    layer = Column(Integer)
    wikidata = Column(UnicodeText)
    note = Column(UnicodeText)
