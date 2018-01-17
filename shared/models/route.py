import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, WheelchairAccess, RouteType, RouteImportance

class RouteState(enum.Enum):
    recommended = 0
    proposed = 1
    alternate = 2
    connection = 3

class RouteService(enum.Enum):
    long_distance = 0

class FerryType(enum.Enum):
    local = 0
    unclassified = 1

class Route(Named):
    __tablename__ = "routes"
    __mapper_args__ = {'polymorphic_identity': 'route', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(RouteType), nullable=False)
    complete = Column(UnicodeText)
    destinations = Column(UnicodeText)
    kct_red = Column(IntEnum(RouteImportance))
    network = Column(UnicodeText)
    note = Column(UnicodeText)
    operator = Column(UnicodeText)
    symbol = Column(UnicodeText)
    kct_yellow = Column(IntEnum(RouteImportance))
    kct_green = Column(IntEnum(RouteImportance))
    kct_blue = Column(IntEnum(RouteImportance))
    alt_name = Column(UnicodeText)
    description = Column(UnicodeText)
    from_ = Column(UnicodeText)
    kct_none = Column(IntEnum(RouteImportance))
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    to = Column(UnicodeText)
    fixme = Column(UnicodeText)
    distance = Column(UnicodeText)
    state = Column(IntEnum(RouteState))
    website = Column(UnicodeText)
    lcn_description = Column(UnicodeText)
    colour = Column(UnicodeText)
    service = Column(IntEnum(RouteService))
    via = Column(UnicodeText)
    public_transport_version = Column(Integer)
    wheelchair = Column(IntEnum(WheelchairAccess))
    text_colour = Column(UnicodeText)
    note_1 = Column(UnicodeText)
    note_2 = Column(UnicodeText)
    trail_type = Column(IntEnum(RouteImportance))
    public_transport = Column(UnicodeText)
    designation = Column(UnicodeText)
    short_name = Column(UnicodeText)
    section = Column(UnicodeText)
    icn_ref = Column(Integer)
    route_master = Column(IntEnum(RouteType))
    bicycle = Column(Boolean)
    foot = Column(Boolean)
    motor_vehicle = Column(Boolean)
    opening_hours = Column(UnicodeText)
    duration = Column(UnicodeText)
    fee = Column(Boolean)
    road_components = Column(Integer)
    ferry = Column(IntEnum(FerryType))
    start_date = Column(UnicodeText)
    a = Column(Integer)
    destination = Column(UnicodeText)
    official_name = Column(UnicodeText)
    opening_date = Column(UnicodeText)
    roundtrip = Column(Boolean)
    nat_ref = Column(UnicodeText)
    kct_white = Column(IntEnum(RouteImportance))
    note_cz = Column(UnicodeText)

