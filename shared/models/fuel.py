from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from sqlalchemy.orm import relationship
from .enums import BuildingType, ShopType
from .entity import Entity

class Fuel(Entity):
    __tablename__ = "fuels"
    __mapper_args__ = {'polymorphic_identity': 'fuel'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    name = Column(UnicodeText)
    operator = Column(UnicodeText)
    brand = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    internet_access_paid = Column(UnicodeText)
    shop = Column(Enum(ShopType))
    phone = Column(UnicodeText)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    building_type = Column(Enum(BuildingType))
    levels = Column(Integer)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    website = Column(UnicodeText)