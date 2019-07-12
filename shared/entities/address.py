from pydantic import BaseModel

class Address(BaseModel):
    place: str = None
    city: str = None
    postcode: int = None
    conscription_number: int = None
    housenumber: str = None
    streetnumber: str = None
    street: str = None
    provisionalnumber: int = None
    suburb: str = None
    housename: str = None

    def __str__(self):
        to_return = ""
        if self.housename:
            to_return = "%s, "%self.housename
        if self.street:
            to_return += "%s %s, %s %s"%(self.street, self.housenumber, self.postcode, self.city)
        else:
            to_return += "%s, %s %s"%(self.housenumber, self.postcode, self.city or self.place)
        return to_return