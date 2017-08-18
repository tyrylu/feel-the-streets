from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from sqlalchemy.orm import relationship
from . import Named

class Theatre(Named):
    __tablename__ = "theatres"
    __mapper_args__ = {'polymorphic_identity': 'theatre'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    is_in = Column(UnicodeText)
    levels = Column(Integer)
    flats = Column(Integer)