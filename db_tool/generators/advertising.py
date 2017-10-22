from .generator import Generator
from shared.models import Advertising

class AdvertisingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Advertising)
        self.renames("advertising", "type")

    @staticmethod
    def accepts(props):
        return "advertising" in props