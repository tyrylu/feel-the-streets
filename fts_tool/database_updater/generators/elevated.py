from .generator import Generator
from shared.models import Elevated

class ElevatedGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Elevated)

    def _prepare_properties(self, entity_spec, props, record):
        props["ele"] = props["ele"].replace("'", "")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "ele" in props
