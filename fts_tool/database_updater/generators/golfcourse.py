from .leisure import LeisureGenerator
from shared.models import GolfCourse

class GolfCourseGenerator(LeisureGenerator):
    def __init__(self):
        super().__init__()
        self.generates(GolfCourse)
        self.renames("golf:course", "golf_course_type")

    @staticmethod
    def accepts(props):
        return LeisureGenerator.accepts(props) and "golf:course" in props