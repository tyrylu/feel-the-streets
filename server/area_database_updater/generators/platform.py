from .generator import Generator
from shared.entities import Platform

class PlatformGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Platform)
        self.renames("route:ref", "route_ref")
        self.renames("indoor:level", "indoor_level")
    @staticmethod
    def accepts(props):
        return "public_transport" in props and props["public_transport"] == "platform"