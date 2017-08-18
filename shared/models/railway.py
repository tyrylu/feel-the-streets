import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from sqlalchemy.orm import relationship
from .enums import CrossingType, BuildingType, RailWayType, TunnelType, BridgeType, Location
from . import Named

class RailWayUsage(enum.Enum):
    unknown = 0
    main = 1
    branch = 2


class RailWay(Named):
    __tablename__ = "rail_ways"
    __mapper_args__ = {'polymorphic_identity': 'rail_way'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(RailWayType), nullable=False)
    gauge = Column(UnicodeText)
    usage = Column(Enum(RailWayUsage))
    electrified = Column(UnicodeText)
    tracks = Column(Integer)
    maxspeed = Column(Integer)
    passenger_lines = Column(Integer)
    service = Column(UnicodeText)
    layer = Column(Integer)
    is_bridge = Column(Enum(BridgeType))
    tunnel = Column(Enum(TunnelType))
    fixme = Column(UnicodeText)
    ele = Column(Integer)
    crossing_light = Column(Boolean)
    crossing_bell = Column(Boolean)
    crossing_barrier = Column(Boolean)
    crossing_type = Column(Enum(CrossingType))
    supervised = Column(Boolean)
    surface = Column(UnicodeText)
    building_type = Column(Enum(BuildingType))
    flats = Column(Integer)
    levels = Column(Integer)
    oneway = Column(Boolean)
    tram_oneway = Column(Boolean)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    cutting = Column(Boolean)
    frequency = Column(Integer)
    voltage = Column(Integer)
    traffic_mode = Column(UnicodeText)
    preferred_direction = Column(UnicodeText)
    wheelchair = Column(Boolean)
    location = Column(Enum(Location))