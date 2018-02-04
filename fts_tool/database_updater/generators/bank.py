from .address_aware import AddressAwareGenerator
from shared.entities import Bank

class BankGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Bank)
        self.unprefixes("building")
        self.unprefixes("contact")
        self.renames("building", "building_type")

        self.renames("payment:contactless", "contactless_payment")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "bank"