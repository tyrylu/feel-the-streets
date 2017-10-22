from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Bench(Entity):
    __tablename__ = "benches"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'bench'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    backrest = Column(Boolean)