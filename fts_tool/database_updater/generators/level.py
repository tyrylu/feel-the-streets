from .named import NamedGenerator
from shared.entities import Level

class LevelGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Level)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "level"