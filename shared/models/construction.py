import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, ConstructionType, RoadType

class Construction(Named):
    __tablename__ = "constructions"
    __mapper_args__ = {'polymorphic_identity': 'construction', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(ConstructionType), nullable=False)
    official_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    bridge = Column(Boolean)
    layer = Column(Integer)
    abandoned_highway = Column(IntEnum(RoadType))
    abandoned_ref = Column(UnicodeText)
    official_en_name = Column(UnicodeText)
    note = Column(UnicodeText)
    official_name_1 = Column(UnicodeText)

