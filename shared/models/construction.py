import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, ConstructionType, RoadType

    
class Construction(Named):
    __tablename__ = "constructions"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'construction'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(ConstructionType), nullable=False)
    official_name = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    bridge = Column(Boolean)
    layer = Column(Integer)
    abandoned_highway = Column(IntEnum(RoadType))
    abandoned_ref = Column(UnicodeText)
    official_en_name = Column(UnicodeText)
    