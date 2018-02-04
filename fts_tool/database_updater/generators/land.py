from .address_aware import AddressAwareGenerator
from shared.entities import Land

class LandGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Land)
        self.renames("landuse", "type")
        self.renames("shop", "shop_type")
        self.renames("meadow", "meadow_type")
        self.renames("natural", "natural_type")
        self.renames("military", "military_type")
        self.renames("uhul:slt", "uhul_slt")
        self.renames("uhul:area", "uhul_area")
        self.renames("uhul:id", "uhul_id")
        self.renames("url", "website")
        self.renames("bridge:structure", "bridge_structure")
        self.renames("barrier:height", "barrier_height")


        self.renames("clc:code", "clc_code")
    @staticmethod
    def accepts(props):
        return "landuse" in props