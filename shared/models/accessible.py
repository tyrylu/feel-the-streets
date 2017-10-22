from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import AccessType, OSMObjectType

class Accessible(Entity):
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __tablename__ = "accessibles"
    __mapper_args__ = {'polymorphic_identity': 'accessible'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(AccessType), nullable=False)