import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from .enums import WaterWayType, TunnelType
from . import Named

class WaterWay(Named):
    __tablename__ = "water_ways"
    __mapper_args__ = {'polymorphic_identity': 'water_way'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(WaterWayType), nullable=False)
    alt_name = Column(UnicodeText)
    tunnel = Column(Enum(TunnelType))
    layer = Column(Integer)
    boats_allowed = Column(Boolean)
    motor_boats_allowed = Column(Boolean)
    service = Column(UnicodeText)
    width = Column(Integer)
    fixme = Column(UnicodeText)
    intermittent = Column(Boolean)
    @property
    def effective_width(self):
        if self.width:
            return self.width
        else:
            return 1