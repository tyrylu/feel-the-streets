from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from . import Named
from .enums import OSMObjectType

class Theatre(Named):
    __tablename__ = "theatres"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'theatre'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    is_in = Column(UnicodeText)
    levels = Column(Integer)
    flats = Column(Integer)