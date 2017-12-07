from .generator import Generator
from shared.models import Surveillance

class SurveillanceGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Surveillance)
        self.renames("surveillance", "type")

    @staticmethod
    def accepts(props):
        return "surveillance" in props