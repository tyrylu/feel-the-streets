from .generator import Generator
from shared.entities import Bench

class BenchGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Bench)

    @staticmethod
    def accepts(props):
        return "bench" in props