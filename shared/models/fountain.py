from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer
from .enums import HistoricType
from . import Named

class Fountain(Named):
    __tablename__ = "fountains"
    __mapper_args__ = {'polymorphic_identity': 'fountain'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    drinking_water = Column(Boolean)
    historic = Column(Enum(HistoricType))