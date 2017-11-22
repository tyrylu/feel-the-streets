import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .leisure import Leisure
from .enums import OSMObjectType

class PlaygroundType(enum.Enum):
    sandpit = 0
    slide = 1
    swing = 2
    basketswing = 3

class Playground(Leisure):
    __tablename__ = "playgrounds"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["leisures.id", "leisures.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'playground'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    playground_type = Column(IntEnum(PlaygroundType))