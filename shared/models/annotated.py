from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType, AccessType, RouteType, BuildingType, ConstructionType, RoofShape, RailWayType

class Annotated(Named):
    __tablename__ = "annotated"
    __mapper_args__ = {'polymorphic_identity': 'annotated', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    note = Column(UnicodeText)
    fixme = Column(UnicodeText)
    website = Column(UnicodeText)
    level = Column(Integer)
    removed_name = Column(UnicodeText)
    building_part = Column(Boolean)
    access = Column(IntEnum(AccessType))
    complete = Column(Boolean)
    route_master = Column(IntEnum(RouteType))
    lock = Column(Boolean)
    historic_building = Column(IntEnum(BuildingType))
    proposed = Column(IntEnum(ConstructionType))
    building_colour = Column(UnicodeText)
    roof_shape = Column(IntEnum(RoofShape))
    disused_railway = Column(IntEnum(RailWayType))
    phone = Column(UnicodeText)
    removed_phone = Column(UnicodeText)
