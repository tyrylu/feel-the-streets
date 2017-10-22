from .generator import Generator
from shared.models import Piste

class PisteGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Piste)
        self.unprefixes("piste")

    @staticmethod
    def accepts(props):
        return "piste:type" in props