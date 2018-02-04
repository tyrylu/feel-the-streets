from .generator import Generator
from shared.entities import SchoolThing

class SchoolThingGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(SchoolThing)
        self.renames("school", "type")

    @staticmethod
    def accepts(props):
        return "school" in props