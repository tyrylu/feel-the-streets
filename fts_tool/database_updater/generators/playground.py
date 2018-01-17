from .leisure import LeisureGenerator
from shared.models import Playground

class PlaygroundGenerator(LeisureGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Playground)
        self.renames("playground", "playground_type")

    @staticmethod
    def accepts(props):
        return LeisureGenerator.accepts(props) and "playground" in props
