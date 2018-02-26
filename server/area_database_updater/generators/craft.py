from .address_aware import AddressAwareGenerator
from shared.entities import Craft

class CraftGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Craft)
        self.renames("craft", "type")
        self.unprefixes("contact")

        self.renames("payment:bitcoin", "bitcoin_payment")
    @staticmethod
    def accepts(props):
        return "craft" in props