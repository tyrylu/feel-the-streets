from .generator import Generator
from shared.models import ProtectedArea

class ProtectedAreaGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(ProtectedArea)
        self.removes("boundary")
        self.renames("leisure", "type")
        self.removes_subtree("eea")
        self.removes("iucn_level")
        self.removes("area:ha")
        self.removes_subtree("protection_title")
    @staticmethod
    def accepts(props):
        return "protection_title" in props or "boundary" in props and props["boundary"] == "protected_area"