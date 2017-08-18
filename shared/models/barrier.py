from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from .enums import BarrierType, AccessType
from . import Named

class Barrier(Named):
    __tablename__ = "barriers"
    __mapper_args__ = {'polymorphic_identity': 'barrier'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(BarrierType), nullable=False)
    foot = Column(Boolean)
    bicycle = Column(Boolean)
    vehicle = Column(Boolean)
    horse = Column(Boolean)
    access = Column(Enum(AccessType))
    entrance = Column(UnicodeText)
    motor_vehicle = Column(UnicodeText)
    note = Column(UnicodeText)
    maxwidth = Column(Integer)
    fence_type = Column(UnicodeText)
    height = Column(Float)
    material = Column(UnicodeText)
    motorcar = Column(Boolean)
    motorcycle = Column(Boolean)
