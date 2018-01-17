from .named import NamedGenerator
from shared.models import Collection

class CollectionGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Collection)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "collection"
