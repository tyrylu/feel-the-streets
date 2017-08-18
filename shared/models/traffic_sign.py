import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Named

class TrafficSignType(enum.Enum):
    city_limit = 0
    maxspeed = 1

class TrafficSign(Named):
    __tablename__ = "traffic_signs"
    __mapper_args__ = {'polymorphic_identity': 'traffic_sign'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(TrafficSignType), nullable=False)
    alt_name = Column(UnicodeText)