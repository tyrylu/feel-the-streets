from .named import NamedGenerator
from shared.entities import Bridge

class BridgeGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Bridge)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "bridge"