from .generator import Generator
from shared.models import TrafficSign

class TrafficSignGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(TrafficSign)
        self.renames("traffic_sign", "type")

        self.renames("traffic_sign:backward", "backward")
    @staticmethod
    def accepts(props):
        return "traffic_sign" in props
