from .generator import Generator
from shared.models import Annotated

class AnnotatedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Annotated)
        self.removes_subtree("note")
        self.removes_subtree("construction")

        self.renames("removed:name", "removed_name")
        self.renames("building:part", "building_part")
        self.renames("historic:building", "historic_building")
        self.renames("building:colour", "building_colour")
        self.renames("roof:shape", "roof_shape")
        self.renames("disused:railway", "disused_railway")
        self.renames("removed:phone", "removed_phone")
    @staticmethod
    def accepts(props):
        return "note" in props
