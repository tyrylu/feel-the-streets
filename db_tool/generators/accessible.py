from .generator import Generator
from shared.models import Accessible

class AccessibleGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Accessible)
        self.renames("access", "type")

    @staticmethod
    def accepts(props):
        return "access" in props