import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from .boundary import Boundary
from .enums import OSMObjectType


class BorderType(enum.Enum):
    nation = 0

class Border(Boundary):
    __tablename__ = "borders"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["boundaries.id", "boundaries.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'border'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    border_type = Column(IntEnum(BorderType))
    is_in = Column(UnicodeText)
    left_country = Column(UnicodeText)
    right_country = Column(UnicodeText)
    uploaded_by = Column(UnicodeText)