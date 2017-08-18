from .generator import Generator
from shared.models import Bunker

class BunkerGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Bunker)
        self.removes("military")
        self.renames("bunker_type", "type")

    @staticmethod
    def accepts(props):
        return "military" in props and props["military"] == "bunker"