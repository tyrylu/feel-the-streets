from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from . import Named
from .enums import OSMObjectType

class Theatre(Named):
    __tablename__ = "theatres"
    __mapper_args__ = {'polymorphic_identity': 'theatre', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    is_in = Column(UnicodeText)
    levels = Column(Integer)
    flats = Column(Integer)