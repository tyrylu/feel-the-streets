import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import HistoricType, OSMObjectType

class Historic(Named):
    __tablename__ = "historic"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'historic'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(HistoricType), nullable=False)
    ele = Column(Float)
    inscription = Column(UnicodeText)
    religion = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    denomination = Column(UnicodeText)
    website = Column(UnicodeText)
    start_date = Column(UnicodeText)
    ruins = Column(Boolean)
    wikidata = Column(UnicodeText)
    heritage = Column(Integer)
    heritage_operator = Column(UnicodeText)
    wikimedia_commons = Column(UnicodeText)
    image = Column(UnicodeText)
    description = Column(UnicodeText)
    