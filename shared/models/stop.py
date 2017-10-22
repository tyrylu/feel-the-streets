import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Float, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class StopType(enum.Enum):
    must_infer = -1
    bus_stop = 0
    bus_station = 1
    tram_stop = 2
    stop = 3
    station = 4
    survey = 5
    disused = 6
    construction = 7
    stop_area = 8
    

class Stop(Named):
    __tablename__ = "stops"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'stop'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(StopType))
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
    trolleybus = Column(Boolean)
    alt_name = Column(UnicodeText)
    route_ref = Column(UnicodeText) # More exactly it is an array of ints...
    local_ref = Column(UnicodeText)
    fixme = Column(UnicodeText)
    ele = Column(Float)
    image = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    ref_name = Column(UnicodeText)
    short_name = Column(UnicodeText)
    bin = Column(Boolean)
    official_name = Column(UnicodeText)
    