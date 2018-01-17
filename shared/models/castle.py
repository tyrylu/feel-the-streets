from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import OSMObjectType

class Castle(Building):
    __tablename__ = "castles"
    __mapper_args__ = {'polymorphic_identity': 'castle', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    type = Column(UnicodeText)
    alt_name_3 = Column(UnicodeText)