from .generator import Generator
from shared.models import Bench

class BenchGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Bench)
        self.removes("bench")

    @staticmethod
    def accepts(props):
        return "bench" in props