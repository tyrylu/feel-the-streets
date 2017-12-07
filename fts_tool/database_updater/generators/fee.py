from .generator import Generator
from shared.models import Fee

class FeeGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Fee)

    @staticmethod
    def accepts(props):
        return "fee" in props