from .address_aware import AddressAwareGenerator
from shared.entities import SocialFacility

class SocialFacilityGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(SocialFacility)
        self.renames("social_facility", "facility_type")
        self.renames("social_facility:for", "expected_users")
        self.renames("building", "building_type")
        self.unprefixes("building")

        self.renames("contact:phone", "phone")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "social_facility"