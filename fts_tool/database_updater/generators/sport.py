from .address_aware import AddressAwareGenerator
from shared.models import Sport

class SportGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Sport)
        self.renames("sport", "type")
        self.renames("opening_hours:url", "opening_hours_url")
        self.removes_subtree("piste")
        self.unprefixes("contact")

    def _prepare_properties(self, entity_spec, props, record):
        props["sport"] = props["sport"].replace("10", "ten_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "sport" in props