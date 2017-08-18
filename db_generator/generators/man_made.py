from .generator import Generator
from shared.models import ManMade

class ManMadeGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(ManMade)
        self.renames("razed:man_made", "type")
        self.renames("man_made", "type")
        self.unprefixes("contact")
        self.removes("observatory:type")

    @staticmethod
    def accepts(props):
        return "razed:man_made" in props or "man_made" in props