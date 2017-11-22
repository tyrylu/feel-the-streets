from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import TrafficCalmingType, OSMObjectType, Surface
from .entity import Entity

class TrafficCalming(Entity):
    __tablename__ = "traffic_calmings"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'traffic_calming'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(TrafficCalmingType), nullable=False)
    note = Column(UnicodeText)
    surface = Column(IntEnum(Surface))