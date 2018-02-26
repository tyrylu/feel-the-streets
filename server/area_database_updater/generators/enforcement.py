from .named import NamedGenerator
from shared.entities import Enforcement

class EnforcementGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Enforcement)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "enforcement"