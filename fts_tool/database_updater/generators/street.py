from .named import NamedGenerator
from shared.entities import Street

class StreetGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Street)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "street"