from .road import RoadGenerator
from shared.models import ServiceRoad

class ServiceRoadGenerator(RoadGenerator):
    def __init__(self):
        super().__init__()
        self.generates(ServiceRoad)
        self.removes_subtree("motor_vehicle")
        self.renames("vehicle:backward", "vehicle_backward")
    @staticmethod
    def accepts(props):
        return RoadGenerator.accepts(props) and props["highway"] == "service"
