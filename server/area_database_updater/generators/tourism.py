from .address_aware import AddressAwareGenerator
from shared.entities import Tourism

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
        self.renames("artwork:type", "artwork_type")
        self.renames("payment:bitcoin", "bitcoin_payment")
        self.renames("description:en", "en_description")
        self.renames("taxon:cs", "taxon_cs")
        self.unprefixes("contact")

        self.renames("artist:wikidata", "artist_wikidata")
        self.renames("note:en", "en_note")
        self.renames("payment:litecoin", "litecoin_payment")
        self.renames("high_water:height", "high_water_height")
        self.renames("alt_name:cs", "alt_name_cs")
    @staticmethod
    def accepts(props):
        return "tourism" in props