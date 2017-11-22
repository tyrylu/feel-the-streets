import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer
from ..sa_types import IntEnum
from .leisure import Leisure
from .enums import OSMObjectType

class GolfCourseType(enum.Enum):
    pitch_and_put = 0
    driving_range = 1

class GolfCourse(Leisure):
    __tablename__ = "golf_courses"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["leisures.id", "leisures.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'golf_course'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    golf_course_type = Column(IntEnum(GolfCourseType))