import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType, Amenity

class DisusedType(enum.Enum):
    quarry = 0
    yes = 1

class Disused(Entity):
    __tablename__ = "disused"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'disused'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(DisusedType), nullable=False)
    denomination = Column(UnicodeText)
    destroyed_amenity = Column(IntEnum(Amenity))
    destroyed_name = Column(UnicodeText)
    end_date = Column(UnicodeText)
    start_date = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    religion = Column(UnicodeText)