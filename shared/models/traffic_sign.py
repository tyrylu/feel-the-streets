import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, TrafficSignType

class TrafficSign(Named):
    __tablename__ = "traffic_signs"
    __mapper_args__ = {'polymorphic_identity': 'traffic_sign', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(TrafficSignType), nullable=False)
    alt_name = Column(UnicodeText)
    maxspeed = Column(Integer)
    backward = Column(Boolean)
