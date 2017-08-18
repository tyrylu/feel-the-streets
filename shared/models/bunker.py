import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from . import Named


class BunkerType(enum.Enum):
    pillbox = 0

class Bunker(Named):
    __tablename__ = "bunkers"
    __mapper_args__ = {'polymorphic_identity': 'bunker'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    website = Column(UnicodeText)
    type = Column(Enum(BunkerType))
    historic = Column(Boolean)