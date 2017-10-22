from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Fee(Entity):
    __tablename__ = "fees"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'fee'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    fee = Column(Boolean)