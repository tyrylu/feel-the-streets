import enum
from .enums import WaterWayType, TunnelType, RoadType, Surface, NoticeFunction, NoticeType, SportType, NoticeImpact, NoticeCategory
from . import Named

class LifeCycle(enum.Enum):
    in_use = 0

class Cemt(enum.Enum):
    Va = 0

class WaterWay(Named):
    type: WaterWayType
    alt_name: str = None
    tunnel: TunnelType = None
    layer: int = None
    boats_allowed: bool = None
    motor_boats_allowed: bool = None
    service: str = None
    width: int = None
    fixme: str = None
    intermittent: bool = None
    destination: str = None
    wikidata: str = None
    note: str = None
    old_name: str = None
    highway: RoadType = None
    surface: Surface = None
    bridge: bool = None
    mtb_scale: int = None
    life_cycle: LifeCycle = None
    start_date: str = None
    area: bool = None
    wikipedia: str = None
    whitewater_section_grade: str = None
    have_riverbank: bool = None
    whitewater_section_name: str = None
    whitewater_rapid_name: str = None
    whitewater_rapid_grade: str = None
    cemt: Cemt = None
    seamark_notice_function: NoticeFunction = None
    seamark_type: NoticeType = None
    cutting: bool = None
    sport: SportType = None
    seamark_notice_impact: NoticeImpact = None
    seamark_notice_category: NoticeCategory = None
    maxspeed: int = None
    seasonal: bool = None
    sac_scale: str = None

    @property
    def effective_width(self):
        if self.width:
            return self.width
        else:
            return 1