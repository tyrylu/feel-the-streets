import enum
from sqlalchemy import Column, Boolean, Enum, Integer, ForeignKey, UnicodeText, Float
from sqlalchemy.orm import relationship
from . import Named

class ClubType(enum.Enum):
    yes = 1
    scuba_diving = 2
    music = 3

class Addressable(Named):
    __tablename__ = "addressables"
    __mapper_args__ = {'polymorphic_identity': 'addressable'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    note = Column(UnicodeText)
    is_in = Column(UnicodeText)
    fixme = Column(UnicodeText)
    website = Column(UnicodeText)
    ele = Column(Float)
    club = Column(Enum(ClubType))
    
    def __str__(self):
        return super().__str__() + (", " + str(self.address) if self.address else "")