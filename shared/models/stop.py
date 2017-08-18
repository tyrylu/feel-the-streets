import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from . import Named

class StopType(enum.Enum):
    must_infer = -1
    bus_stop = 0
    bus_station = 1
    tram_stop = 2
    stop = 3
    station = 4


class Stop(Named):
    __tablename__ = "stops"
    __mapper_args__ = {'polymorphic_identity': 'stop'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(StopType))
    bus = Column(Boolean)
    tram = Column(Boolean)
    train = Column(Boolean)
    old_name = Column(UnicodeText)
    has_shelter = Column(Boolean)
    covered = Column(Boolean)
    bench = Column(Boolean)
    operator = Column(UnicodeText)
    tactile_paving = Column(Boolean)
    opening_hours = Column(UnicodeText)
    network = Column(UnicodeText)
    layer = Column(Integer)
    building = Column(Boolean)
    area = Column(Boolean)
    zone = Column(Integer)
    wheelchair = Column(Boolean)
    note = Column(UnicodeText)