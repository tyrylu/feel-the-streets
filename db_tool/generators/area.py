from .address_aware import AddressAwareGenerator
from shared.models import Area

class AreaGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Area)
        self.renames("area", "type")
        self.renames("highway", "type")
    @staticmethod
    def accepts(props):
        return "area" in props and props["area"] == "yes"