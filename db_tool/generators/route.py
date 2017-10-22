from .generator import Generator
from shared.models import Route

class RouteGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Route)
        self.renames("route", "type")
        self.renames("from", "from_")
        self.renames("lcn:description", "lcn_description")
        self.renames("public_transport:version", "public_transport_version")
        self.unprefixes("osmc")

    @staticmethod
    def accepts(props):
        return "route" in props