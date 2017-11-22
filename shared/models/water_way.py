import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import WaterWayType, TunnelType, OSMObjectType, RoadType, Surface
from . import Named

class LifeCycle(enum.Enum):
    in_use = 0
class WaterWay(Named):
    __tablename__ = "water_ways"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'water_way'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(WaterWayType), nullable=False)
    alt_name = Column(UnicodeText)
    tunnel = Column(IntEnum(TunnelType))
    layer = Column(Integer)
    boats_allowed = Column(Boolean)
    motor_boats_allowed = Column(Boolean)
    service = Column(UnicodeText)
    width = Column(Integer)
    fixme = Column(UnicodeText)
    intermittent = Column(Boolean)
    destination = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    note = Column(UnicodeText)
    old_name = Column(UnicodeText)
    highway = Column(IntEnum(RoadType))
    surface = Column(IntEnum(Surface))
    bridge = Column(Boolean)
    mtb_scale = Column(Integer)
    life_cycle = Column(IntEnum(LifeCycle))
    start_date = Column(UnicodeText)
    area = Column(Boolean)
    
    @property
    def effective_width(self):
        if self.width:
            return self.width
        else:
            return 1