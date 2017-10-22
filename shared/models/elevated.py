from sqlalchemy import Column, ForeignKeyConstraint, Integer, Float
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Elevated(Entity):
    __tablename__ = "elevated"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'elevated'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    ele = Column(Float)