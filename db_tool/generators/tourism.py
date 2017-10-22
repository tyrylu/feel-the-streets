from .address_aware import AddressAwareGenerator
from shared.models import Tourism

class TourismGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Tourism)
        self.renames("tourism", "type")
        self.renames("information", "information_type")
        self.renames("url", "website")
        self.renames("barrier", "barrier_type")
        self.renames("building:part", "building_part")
        self.renames("internet_access:fee", "internet_access_fee")
        self.renames("roof:height", "roof_height")
        self.renames("roof:shape", "roof_shape")
        self.renames("heritage:operator", "heritage_operator")
        self.unprefixes("contact")
        self.removes("alt_ref")
        self.removes("mtb")
        self.removes_subtree("tower")
        self.removes_subtree("building:ruian")

    @staticmethod
    def accepts(props):
        return "tourism" in props