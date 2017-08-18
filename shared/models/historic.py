import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Float, Integer, UnicodeText
from . import Named
from .enums import HistoricType

class Historic(Named):
    __tablename__ = "historic"
    __mapper_args__ = {'polymorphic_identity': 'historic'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(HistoricType), nullable=False)
    ele = Column(Float)
    inscription = Column(UnicodeText)
    religion = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    denomination = Column(UnicodeText)
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    ruins = Column(Boolean)
    wikidata = Column(UnicodeText)
