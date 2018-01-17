import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .boundary import Boundary
from .enums import OSMObjectType, WaterWayType

class BorderType(enum.Enum):
    nation = 0

class Border(Boundary):
    __tablename__ = "borders"
    __mapper_args__ = {'polymorphic_identity': 'border', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("boundaries.id"), primary_key=True)
    border_type = Column(IntEnum(BorderType))
    is_in = Column(UnicodeText)
    left_country = Column(UnicodeText)
    right_country = Column(UnicodeText)
    uploaded_by = Column(UnicodeText)
    waterway = Column(IntEnum(WaterWayType))
    boat = Column(Boolean)
    layer = Column(Integer)
