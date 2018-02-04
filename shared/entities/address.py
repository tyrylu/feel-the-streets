from pydantic import BaseModel

class Address(BaseModel):
    place: str = None
    city: str = None
    post_code: int = None
    conscription_number: int = None
    house_number: str = None
    street_number: str = None
    street: str = None
    provisional_number: int = None
    suburb: str = None
    house_name: str = None

    def __bool__(self):
        return self.place is not None or self.city is not None or self.post_code is not None or self.conscription_number is not None or self.street_number is not None or self.house_number is not None or self.street is not None or self.provisional_number is not None or self.house_name is not None or self.suburb is not None

    def __str__(self):
        to_return = ""
        if self.house_name:
            to_return = "%s, "%self.house_name
        to_return += "%s %s, %s %s"%(self.street, self.house_number, self.post_code, self.city)
        return to_return