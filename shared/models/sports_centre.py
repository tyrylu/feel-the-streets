from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import OSMObjectType

class SportsCentre(Building):
    __tablename__ = "sport_centers"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["buildings.id", "buildings.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'sport_center'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    int_name = Column(UnicodeText)