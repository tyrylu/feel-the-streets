from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Road
from .enums import Inclination, LeisureType, AccessType, OSMObjectType, BuildingType, RouteImportance

class Track(Road):
    __tablename__ = "tracks"
    __mapper_args__ = {'polymorphic_identity': 'track', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("roads.id"), primary_key=True)
    motorcar_allowed = Column(IntEnum(AccessType))
    leisure = Column(IntEnum(LeisureType))
    mtb_scale = Column(Integer)
    mtb_scale_uphill = Column(Integer)
    forestry = Column(Boolean)
    bicycle_class = Column(Integer)
    ticks_description = Column(UnicodeText)
    motor_vehicle_note = Column(UnicodeText)
    proposed_segregated = Column(Boolean)
    steep_incline = Column(Boolean)
    trasa = Column(Integer)
    sprint_lanes = Column(Integer)
    todo = Column(UnicodeText)
    kct_barva = Column(IntEnum(RouteImportance))
    designation = Column(UnicodeText)

