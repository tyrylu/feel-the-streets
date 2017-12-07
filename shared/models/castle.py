from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import OSMObjectType

class Castle(Building):
    __tablename__ = "castles"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["buildings.id", "buildings.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'castle'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(UnicodeText)
    alt_name_3 = Column(UnicodeText)