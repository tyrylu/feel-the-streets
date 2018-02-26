from .address_aware import AddressAwareGenerator
from shared.entities import Amenity

class AmenityGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Amenity)
        self.renames("amenity", "type")
        self.renames("community_centre:for", "community_centre_for")
        self.renames("place", "place_type")
        self.renames("diet:vegetarian", "vegetarian_diet")
        self.renames("internet_access:fee", "internet_access_fee")
        self.renames("internet_access:ssid", "internet_access_ssid")
        self.renames("capacity:car", "car_capacity")
        self.renames("authentication:nfc", "nfc_authentication")
        self.replaces_property_value("post_code", " ", "")
        self.unprefixes("contact")
        self.renames("toilets:disposal", "toilets_disposal")
        self.renames("socket:schuko", "schuko_socket")
        self.renames("socket:schuko:voltage", "schuko_socket_voltage")
        self.renames("socket:type2:voltage", "type2_socket_voltage")
        self.renames("toilets:wheelchair", "wheelchair_toilets")
        self.renames("diet:vegan", "vegan_diet")
        self.renames("short_name:en", "short_name_en")
        self.renames("socket:chademo", "chademo_socket")
        self.renames("socket:chademo:power", "chademo_socket_power")
        self.renames("socket:type2", "type2_socket")
        self.renames("socket:schuko:current", "schuko_socket_current")
        
    @staticmethod
    def accepts(props):
        return "amenity" in props and "building" not in props