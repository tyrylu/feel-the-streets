from sqlalchemy import Column, ForeignKey, Integer, Boolean, UnicodeText
from . import Addressable

class ATM(Addressable):
    __tablename__ = "atms"
    __mapper_args__ = {'polymorphic_identity': 'atm'}
    id = Column(Integer, ForeignKey("addressables.id"), primary_key=True)
    operator = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    contact_website = Column(UnicodeText)
    fee = Column(UnicodeText)
    description = Column(UnicodeText)
    drive_through = Column(Boolean)
    phone = Column(UnicodeText)