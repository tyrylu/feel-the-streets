from .building import BuildingGenerator
from shared.models import HealthCare

class HealthCareGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(HealthCare)
        self.renames("healthcare", "type")
        self.unprefixes("healthcare")

    @staticmethod
    def accepts(props):
        return BuildingGenerator.accepts(props) and "healthcare" in props