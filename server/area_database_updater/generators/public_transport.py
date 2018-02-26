from .named import NamedGenerator
from shared.entities import PublicTransport

class PublicTransportGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(PublicTransport)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "public_transport"