{% if address_aware %}
{% set base_class = "AddressAwareGenerator" %}
from .address_aware import AddressAwareGenerator
{% else %}
{% set base_class = "Generator" %}
from .generator import Generator
{% endif %}
from shared.models import {{ entity_class }}

class {{ generator_class }}({{ base_class }}):
    def __init__(self):
        super().__init__()
        self.generates({{ entity_class }})

    @staticmethod
    def accepts(props):
        return {{ acceptance_check }}