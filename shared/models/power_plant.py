from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Building
from .enums import OSMObjectType

class PowerPlant(Building):
    __tablename__ = "power_plants"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["buildings.id", "buildings.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'power_plant'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    electricity_output = Column(UnicodeText)
    frequency= Column(Integer)
    