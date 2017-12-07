from .address_aware import AddressAwareGenerator
from shared.models import Office

class OfficeGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Office)
        self.renames("office", "type")
        self.renames("payment:bitcoin", "bitcoin_payment")
        self.renames("building:roof:material", "roof_material")
        self.renames("building:roof:shape", "roof_shape")
        self.renames("building:roof:height", "roof_height")
        self.renames("building:roof:colour", "roof_colour")
        self.removes("building")
        self.renames("roof:material", "roof_material")
        self.renames("roof:shape", "roof_shape")
        self.renames("roof:height", "roof_height")
        self.renames("roof:colour", "roof_colour")
        
        self.removes_subtree("ruian")
        self.unprefixes("building")
        self.unprefixes("contact")
        self.removes("uir_adr:adresa_kod")

    @staticmethod
    def accepts(props):
        return "office" in props