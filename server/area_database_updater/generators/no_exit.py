from .generator import Generator
from shared.entities import NoExit

class NoExitGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(NoExit)

    @staticmethod
    def accepts(props):
        return "noexit" in props