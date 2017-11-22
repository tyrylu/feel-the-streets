from .address_aware import AddressAwareGenerator
from shared.models import Office

class OfficeGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Office)
        self.renames("office", "type")
        self.renames("payment:bitcoin", "bitcoin_payment")
        
        self.removes("building")
        self.removes_subtree("ruian")
        self.unprefixes("building")
        self.unprefixes("contact")
        self.removes("uir_adr:adresa_kod")

    @staticmethod
    def accepts(props):
        return "office" in props