import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .leisure import Leisure
from .enums import OSMObjectType

class GolfCourseType(enum.Enum):
    pitch_and_put = 0
    driving_range = 1
    pitch_and_putt = 2

class GolfCourse(Leisure):
    __tablename__ = "golf_courses"
    __mapper_args__ = {'polymorphic_identity': 'golf_course', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("leisures.id"), primary_key=True)
    golf_course_type = Column(IntEnum(GolfCourseType))
    par = Column(UnicodeText)
