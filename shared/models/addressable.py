import enum
from sqlalchemy import Column, Boolean, Integer, ForeignKey, ForeignKeyConstraint, UnicodeText, Float
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from . import Named
from .enums import OSMObjectType

class ClubType(enum.Enum):
    yes = 1
    scuba_diving = 2
    music = 3
    board_games = 4
    

class Addressable(Named):
    __tablename__ = "addressables"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'addressable'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    note = Column(UnicodeText)
    is_in = Column(UnicodeText)
    fixme = Column(UnicodeText)
    website = Column(UnicodeText)
    ele = Column(Float)
    club = Column(IntEnum(ClubType))
    
    def __str__(self):
        return super().__str__() + (", " + str(self.address) if self.address else "")