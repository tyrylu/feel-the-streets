from .leisure import LeisureGenerator
from shared.entities import GolfCourse

class GolfCourseGenerator(LeisureGenerator):
    def __init__(self):
        super().__init__()
        self.generates(GolfCourse)
        self.renames("golf:course", "golf_course_type")

        self.renames("golf:par", "par")
    @staticmethod
    def accepts(props):
        return LeisureGenerator.accepts(props) and "golf:course" in props