from .address_aware import AddressAwareGenerator
from shared.models import Fuel

class FuelGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Fuel)
        self.removes("amenity")
        self.removes_subtree("fuel")
        self.renames("internet_access:fee", "internet_access_paid")
        self.renames("building", "building_type")
        self.removes_subtree("ruian")
        self.unprefixes("building")
        
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "fuel"