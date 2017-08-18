from .generator import Generator
from shared.models import Named

class NamedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Named)

    @staticmethod
    def accepts(props):
        return "name" in props