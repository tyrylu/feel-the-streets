from sqlalchemy import Column, ForeignKey, Float, Integer, UnicodeText
from . import Natural

class Tree(Natural):
    __tablename__ = "trees"
    __mapper_args__ = {'polymorphic_identity': 'tree'}
    id = Column(Integer, ForeignKey("naturals.id"), primary_key=True)
    taxon = Column(UnicodeText)
    genus = Column(UnicodeText)
    leaf_type = Column(UnicodeText)
    leaf_cycle = Column(UnicodeText)
    species = Column(UnicodeText)
    taxon_cs = Column(UnicodeText)
    genus_cs = Column(UnicodeText)
    height = Column(Float)
    denotation = Column(UnicodeText)
    circumference = Column(Float)
    species_cs = Column(UnicodeText)