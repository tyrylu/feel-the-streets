from .address_aware import AddressAwareGenerator
from shared.models import Bank

class BankGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Bank)
        self.removes("amenity")
        self.removes("bic")
        self.removes_subtree("ruian")
        self.unprefixes("building")
        self.unprefixes("contact")
        self.renames("building", "building_type")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "bank"