from .named import NamedGenerator
from shared.models import AssociatedStreet

class AssociatedStreetGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(AssociatedStreet)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "associatedStreet"
