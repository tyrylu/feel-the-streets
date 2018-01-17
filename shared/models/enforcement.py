from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, TrafficSignType

class Enforcement(Named):
    __tablename__ = "enforcements"
    __mapper_args__ = {'polymorphic_identity': 'enforcement', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    enforcement = Column(IntEnum(TrafficSignType))
    maxspeed = Column(Integer)
