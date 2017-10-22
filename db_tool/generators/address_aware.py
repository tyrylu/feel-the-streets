from .utils import create_address
from .generator import Generator

class AddressAwareGenerator(Generator):
    def _prepare_properties(self, entity_spec, props, record):
        props = super()._prepare_properties(entity_spec, props, record)
        props["address"] = create_address(props)
        return props