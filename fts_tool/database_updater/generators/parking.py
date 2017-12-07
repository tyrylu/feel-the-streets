from .address_aware import AddressAwareGenerator
from shared.models import Parking

class ParkingGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Parking)
        self.removes("amenity")
        self.removes_subtree("building:ruian")
        self.renames("building", "building_type")
        self.renames("capacity:disabled", "capacity_for_disabled")
        self.renames("building:levels", "building_levels")
        self.renames("capacity:parent", "capacity_for_parents")
        self.renames("capacity:women", "capacity_for_women")
        self.renames("url", "website")
        self.renames("fee", "paid") # Don't ask me if there is a difference.
        self.renames("parking", "type")
        
    def _prepare_properties(self, entity_spec, props, record):
        if "parking" in props: props["parking"] = props["parking"].replace("-", "_")
        return super()._prepare_properties(entity_spec, props, record)
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "parking" or "parking" in props