from sqlalchemy import Column, ForeignKey, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Natural
from .enums import OSMObjectType

class Tree(Natural):
    __tablename__ = "trees"
    __mapper_args__ = {'polymorphic_identity': 'tree', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("naturals.id"), primary_key=True)
    taxon = Column(UnicodeText)
    genus = Column(UnicodeText)
    species = Column(UnicodeText)
    taxon_cs = Column(UnicodeText)
    genus_cs = Column(UnicodeText)
    denotation = Column(UnicodeText)
    circumference = Column(Float)
    species_cs = Column(UnicodeText)
    start_date = Column(UnicodeText)
    diameter_crown = Column(Integer)
    genus_en = Column(UnicodeText)
    comment = Column(UnicodeText)
