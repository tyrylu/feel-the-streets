from .generator import Generator
from shared.models import Steps

class StepsGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Steps)
        self.removes("highway")
        self.renames("bycicles", "bycicles_allowed")
        self.renames("incline", "direction")
        self.renames("mtb:scale", "mtb_scale")
        self.renames("mtb:scale:uphill", "mtb_scale_uphill")
        self.renames("handrail:left", "left_handrail")
        self.renames("handrail:right", "right_handrail")
        self.renames("handrail:center", "center_handrail")
        self.renames("step:condition", "step_condition")
        self.renames("step.condition", "step_condition")
        self.renames("step:height", "step_height")
        self.renames("step.height", "step_height")
        self.renames("step:length", "step_length")
        self.renames("step.length", "step_length")
        self.removes("steps")
        self.removes_subtree("ramp")
    @staticmethod
    def accepts(props):
        return "highway" in props and props["highway"] == "steps" or "step_count" in props or "step.condition" in props
