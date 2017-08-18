from .address_aware import AddressAwareGenerator
from shared.models import Amenity

class AmenityGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Amenity)
        self.renames("amenity", "type")
        self.renames("community_centre:for", "community_centre_for")
        self.renames("place", "place_type")
        self.renames("diet:vegetarian", "vegetarian_diet")
        self.removes_subtree("currency")
        self.removes_subtree("payment")
        self.removes_subtree("note")
        self.removes("source_ref")
        self.removes("wikidata")
        self.unprefixes("contact")

    @staticmethod
    def accepts(props):
        return "amenity" in props and "building" not in props