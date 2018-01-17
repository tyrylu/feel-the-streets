from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class DemolishedBuilding(Entity):
    __tablename__ = "demolished_buildings"
    __mapper_args__ = {'polymorphic_identity': 'demolished_building', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    fixme = Column(UnicodeText)

