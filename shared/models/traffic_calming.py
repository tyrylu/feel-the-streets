from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import TrafficCalmingType, OSMObjectType, Surface, AccessType
from .entity import Entity

class TrafficCalming(Entity):
    __tablename__ = "traffic_calmings"
    __mapper_args__ = {'polymorphic_identity': 'traffic_calming', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(TrafficCalmingType), nullable=False)
    note = Column(UnicodeText)
    surface = Column(IntEnum(Surface))
    maxspeed = Column(Integer)
    level = Column(Integer)
    fixme = Column(UnicodeText)
    bicycle = Column(IntEnum(AccessType))
