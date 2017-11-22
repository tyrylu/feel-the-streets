from .{{ superclass_module }} import {{ superclass }}
from shared.models import {{ entity_class }}

class {{ generator_class }}({{ superclass }}):
    def __init__(self):
        super().__init__()
        self.generates({{ entity_class }})

    @staticmethod
    def accepts(props):
        return {{ acceptance_check }}