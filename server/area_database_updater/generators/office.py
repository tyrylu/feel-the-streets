from .address_aware import AddressAwareGenerator
from shared.entities import Office

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
        self.renames("roof:material", "roof_material")
        self.renames("roof:shape", "roof_shape")
        self.renames("roof:height", "roof_height")
        self.renames("roof:colour", "roof_colour")

        self.unprefixes("building")
        self.unprefixes("contact")

        self.renames("description:en", "description_en")
    @staticmethod
    def accepts(props):
        return "office" in props