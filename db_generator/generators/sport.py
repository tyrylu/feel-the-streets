from .generator import Generator
from shared.models import Sport

class SportGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Sport)
        self.renames("sport", "type")
        self.removes_subtree("piste")

    def _prepare_properties(self, entity_spec, props, record):
        props["sport"] = props["sport"].replace("10", "ten_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "sport" in props