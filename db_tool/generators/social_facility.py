from .address_aware import AddressAwareGenerator
from shared.models import SocialFacility

class SocialFacilityGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(SocialFacility)
        self.removes("amenity")
        self.renames("social_facility", "facility_type")
        self.renames("social_facility:for", "expected_users")
        self.renames("building", "building_type")
        self.renames("building:flats", "flats")
        self.removes_subtree("building:ruian")
        self.removes_subtree("health_specialty")

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "social_facility"