import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Entity
from .enums import OSMObjectType, SurveillanceType, SurveillanceKind, SurveillanceZone

class Surveillance(Entity):
    __tablename__ = "surveillances"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'surveillance'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(SurveillanceType))
    kind = Column(IntEnum(SurveillanceKind))
    zone = Column(IntEnum(SurveillanceZone))