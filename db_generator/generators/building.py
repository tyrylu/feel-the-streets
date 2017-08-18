from .address_aware import AddressAwareGenerator
from shared.models import Building

class BuildingGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Building)
        self.unprefixes("building")
        self.renames("roof:height", "roof_height")
        self.renames("roof:shape", "roof_shape")
        self.renames("internet_access:fee", "internet_access_fee")
        self.renames("information", "information_type")
        self.renames("webpage", "website")
        self.renames("url", "website")
        self.renames("diet:vegetarian", "vegetarian_diet")
        self.removes("building")
        self.removes_subtree("ref")
        self.removes_subtree("ruian")
        self.removes_subtree("isced")
        self.removes_subtree("uir_adr")
        self.removes_subtree("wikipedia")
        self.removes_subtree("old_name")
        self.removes_subtree("alt_name")
        self.removes("ruian")
        self.renames("community_centre:for", "community_centre_for")
        self.renames("leisure", "leisure_type")
        self.renames("tourism", "tourism_type")
        self.renames("industrial", "industrial_type")
        self.unprefixes("contact")
        self.renames("historic", "historic_type")

        

    @staticmethod
    def accepts(props):
        return ("building" in props and "aerialway" not in props) or "shop" in props or "building:levels" in props or ("amenity" in props and props["amenity"] in {"kindergarten", "school", "college", "hospital", "restaurant"})