from .generator import Generator
from shared.models import Steps

class StepsGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Steps)
        self.removes("highway")
        self.renames("bycicles", "bycicles_allowed")
        self.renames("incline", "direction")
        self.removes_subtree("ramp")
    @staticmethod
    def accepts(props):
        return "highway" in props and props["highway"] == "steps" or "step_count" in props