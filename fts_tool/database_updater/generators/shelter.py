from .generator import Generator
from shared.models import Shelter

class ShelterGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Shelter)
        self.removes("amenity")
        self.renames("shelter_type", "type")
        self.removes_subtree("building:ruian")
        self.renames("internet_access:ssid", "internet_access_ssid")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "shelter"
