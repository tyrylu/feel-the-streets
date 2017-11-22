from sqlalchemy import Column, ForeignKeyConstraint, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Natural
from .enums import OSMObjectType

class Tree(Natural):
    __tablename__ = "trees"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["naturals.id", "naturals.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'tree'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    taxon = Column(UnicodeText)
    genus = Column(UnicodeText)
    leaf_cycle = Column(UnicodeText)
    species = Column(UnicodeText)
    taxon_cs = Column(UnicodeText)
    genus_cs = Column(UnicodeText)
    height = Column(Float)
    denotation = Column(UnicodeText)
    circumference = Column(Float)
    species_cs = Column(UnicodeText)
