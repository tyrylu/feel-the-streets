from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, BarrierType, Denomination

class Graveyard(Named):
    __tablename__ = "graveyards"
    __mapper_args__ = {'polymorphic_identity': 'graveyard', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    religion = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    barrier = Column(IntEnum(BarrierType))
    denomination = Column(IntEnum(Denomination))
    opening_hours = Column(UnicodeText)
