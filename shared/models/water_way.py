import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import WaterWayType, TunnelType, OSMObjectType, RoadType, Surface, NoticeFunction, NoticeType, SportType, NoticeImpact, NoticeCategory
from . import Named

class LifeCycle(enum.Enum):
    in_use = 0

class Cemt(enum.Enum):
    Va = 0

class WaterWay(Named):
    __tablename__ = "water_ways"
    __mapper_args__ = {'polymorphic_identity': 'water_way', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
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
    wikipedia = Column(UnicodeText)
    whitewater_section_grade = Column(UnicodeText)
    have_riverbank = Column(Boolean)
    whitewater_section_name = Column(UnicodeText)
    whitewater_rapid_name = Column(UnicodeText)
    whitewater_rapid_grade = Column(UnicodeText)
    cemt = Column(IntEnum(Cemt))
    seamark_notice_function = Column(IntEnum(NoticeFunction))
    seamark_type = Column(IntEnum(NoticeType))
    cutting = Column(Boolean)
    sport = Column(IntEnum(SportType))
    seamark_notice_impact = Column(IntEnum(NoticeImpact))
    seamark_notice_category = Column(IntEnum(NoticeCategory))
    maxspeed = Column(Integer)
    seasonal = Column(Boolean)
    sac_scale = Column(UnicodeText)

    @property
    def effective_width(self):
        if self.width:
            return self.width
        else:
            return 1
