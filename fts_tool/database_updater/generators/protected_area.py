from .generator import Generator
from shared.entities import ProtectedArea

class ProtectedAreaGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(ProtectedArea)
        self.renames("leisure", "type")
        self.renames("description:cz", "description_cz")
    @staticmethod
    def accepts(props):
        return "protection_title" in props or "boundary" in props and props["boundary"] == "protected_area"