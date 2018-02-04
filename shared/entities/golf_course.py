import enum
from .leisure import Leisure

class GolfCourseType(enum.Enum):
    pitch_and_put = 0
    driving_range = 1
    pitch_and_putt = 2

class GolfCourse(Leisure):
    golf_course_type: GolfCourseType = None
    par: str = None