import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from . import Named
from .enums import BuildingType
class TransportRelationship(enum.Enum):
    none = 0
    platform = 1
    tram_stop = 2

class Platform(Named):
    __tablename__ = "platforms"
    __mapper_args__ = {'polymorphic_identity': 'platform'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    train = Column(Boolean)
    bus = Column(Boolean)
    tram = Column(Boolean)
    railway = Column(Enum(TransportRelationship))
    shelter = Column(Boolean)
    bench = Column(Boolean)
    network = Column(UnicodeText)
    operator = Column(UnicodeText)
    surface = Column(UnicodeText)
    lit = Column(Boolean)
    wheelchair = Column(Boolean)
    covered = Column(Boolean)
    building = Column(Enum(BuildingType))
