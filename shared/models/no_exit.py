from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class NoExit(Entity):
    __tablename__ = "no_exits"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'no_exit'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)