from .road import RoadGenerator
from shared.entities import ServiceRoad

class ServiceRoadGenerator(RoadGenerator):
    def __init__(self):
        super().__init__()
        self.generates(ServiceRoad)
        self.renames("vehicle:backward", "vehicle_backward")
    @staticmethod
    def accepts(props):
        return RoadGenerator.accepts(props) and props["highway"] == "service"