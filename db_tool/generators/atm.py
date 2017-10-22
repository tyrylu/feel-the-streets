from .address_aware import AddressAwareGenerator
from shared.models import ATM

class ATMGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(ATM)
        self.removes("amenity")
        self.renames("contact:website", "contact_website")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "atm"