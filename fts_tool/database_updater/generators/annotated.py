from .generator import Generator
from shared.models import Annotated

class AnnotatedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Annotated)
        self.removes_subtree("note")
        self.removes_subtree("construction")

    @staticmethod
    def accepts(props):
        return "note" in props