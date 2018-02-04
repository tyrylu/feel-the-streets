from . import OSMEntity

class Named(OSMEntity):
    name: str = None
    
    def __str__(self):
        inherited = super().__str__()
        if self.name:
            inherited += " " + self.name
        return  inherited