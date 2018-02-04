from .address_aware import AddressAwareGenerator
from shared.entities import ATM

class ATMGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(ATM)
        self.renames("contact:website", "contact_website")

        self.renames("atm:bitcoin", "bitcoin")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "atm"