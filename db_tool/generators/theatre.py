from .address_aware import AddressAwareGenerator
from shared.models import Theatre

class TheatreGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Theatre)
        self.removes("amenity")
        self.removes("building")
        self.removes_subtree("building:ruian")
        self.unprefixes_properties("building")
        
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "theatre"