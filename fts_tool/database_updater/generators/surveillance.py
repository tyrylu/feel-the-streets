from .generator import Generator
from shared.entities import Surveillance

class SurveillanceGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Surveillance)
        self.renames("surveillance", "type")

        self.renames("camera:mount", "camera_mount")
        self.renames("camera:direction", "camera_direction")
        self.renames("surveillance:zone", "surveillance_zone")
    @staticmethod
    def accepts(props):
        return "surveillance" in props