import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, TourismType, TransformerType, PowerType, InfoType

class Pole(Named):
    __tablename__ = "poles"
    __mapper_args__ = {'polymorphic_identity': 'pole', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    transformer_type = Column(IntEnum(TransformerType))
    voltage = Column(UnicodeText)
    operator = Column(UnicodeText)
    note = Column(UnicodeText)
    fixme = Column(UnicodeText)
    hiking = Column(Boolean)
    tourism = Column(IntEnum(TourismType))
    pole = Column(IntEnum(PowerType))
    disused = Column(Boolean)
    ele = Column(Integer)
    information = Column(IntEnum(InfoType))
