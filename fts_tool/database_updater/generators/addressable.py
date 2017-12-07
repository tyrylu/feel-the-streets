from .address_aware import AddressAwareGenerator
from shared.models import Addressable

class AddressableGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Addressable)
        self.removes_subtree("uir_adr")

    @staticmethod
    def accepts(props):
        return "addr:housenumber" in props