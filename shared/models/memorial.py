import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Historic

class MemorialType(enum.Enum):
    unknown = 0
    plaque = 1

class MemorialKind(enum.Enum):
    unknown = 0
    war_memorial = 1
    plaque = 2
    statue = 3

class Memorial(Historic):
    __tablename__ = "memorials"
    __mapper_args__ = {'polymorphic_identity': 'memorial'}
    id = Column(Integer, ForeignKey("historic.id"), primary_key=True)
    memorial_type = Column(Enum(MemorialType))
    memorial_kind = Column(Enum(MemorialKind))
    url = Column(UnicodeText)
