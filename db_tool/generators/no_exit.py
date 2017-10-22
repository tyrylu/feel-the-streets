from .generator import Generator
from shared.models import NoExit

class NoExitGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(NoExit)
        self.removes("noexit")

    @staticmethod
    def accepts(props):
        return "noexit" in props