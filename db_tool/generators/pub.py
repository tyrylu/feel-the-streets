from .address_aware import AddressAwareGenerator
from shared.models import Pub

class PubGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Pub)
        self.removes("amenity")
        self.removes("public")
        self.unprefixes("contact")
        self.removes("building")
        self.removes_subtree("ruian")
        self.unprefixes("building")
        self.removes("uir_adr:adresa_kod")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "pub"