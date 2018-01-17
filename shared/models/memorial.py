import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Historic
from .enums import OSMObjectType, MemorialKind

class Memorial(Historic):
    __tablename__ = "memorials"
    __mapper_args__ = {'polymorphic_identity': 'memorial', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("historic.id"), primary_key=True)
    memorial_kind = Column(IntEnum(MemorialKind))
    url = Column(UnicodeText)
    text = Column(UnicodeText)
    network = Column(UnicodeText)
    # Make it a date in a later pass
    person_date_of_death = Column(UnicodeText)
    wikipedia_en = Column(UnicodeText)
    level = Column(Integer)
    inscription_cs = Column(UnicodeText)
    fixme = Column(UnicodeText)
