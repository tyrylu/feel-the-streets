from sqlalchemy import Column, UnicodeText, Integer, String
from . import Base

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    place = Column(UnicodeText)
    city = Column(UnicodeText)
    post_code = Column(Integer)
    conscription_number = Column(Integer)
    house_number = Column(String(128))
    street_number = Column(String(64))
    street = Column(UnicodeText)
    provisional_number = Column(Integer)
    suburb = Column(UnicodeText)
    house_name = Column(UnicodeText)

    def __bool__(self):
        return self.place is not None or self.city is not None or self.post_code is not None or self.conscription_number is not None or self.street_number is not None or self.house_number is not None or self.street is not None or self.provisional_number is not None or self.house_name is not None or self.suburb is not None

    def __str__(self):
        to_return = ""
        if self.house_name:
            to_return = "%s, "%self.house_name
        to_return += "%s %s, %s %s"%(self.street, self.house_number, self.post_code, self.city)
        return to_return