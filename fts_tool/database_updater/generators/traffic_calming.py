from .generator import Generator
from shared.models import TrafficCalming

class TrafficCalmingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(TrafficCalming)
        self.renames("traffic_calming", "type")

    @staticmethod
    def accepts(props):
        return "traffic_calming" in props
