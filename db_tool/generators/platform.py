from .generator import Generator
from shared.models import Platform

class PlatformGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Platform)
        self.renames("route:ref", "route_ref")
        self.removes("public_transport")
        self.removes("highway")
        self.removes_subtree("building")
    @staticmethod
    def accepts(props):
        return "public_transport" in props and props["public_transport"] == "platform"
