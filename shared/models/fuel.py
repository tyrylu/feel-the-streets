from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import BuildingType, ShopType, OSMObjectType, WheelchairAccess, RoofShape, AccessType
from .entity import Entity

class Fuel(Entity):
    __tablename__ = "fuels"
    __mapper_args__ = {'polymorphic_identity': 'fuel', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    name = Column(UnicodeText)
    operator = Column(UnicodeText)
    brand = Column(UnicodeText)
    opening_hours = Column(UnicodeText)
    internet_access = Column(UnicodeText)
    internet_access_paid = Column(UnicodeText)
    shop = Column(IntEnum(ShopType))
    phone = Column(UnicodeText)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    building_type = Column(IntEnum(BuildingType))
    levels = Column(Integer)
    note = Column(UnicodeText)
    start_date = Column(UnicodeText)
    website = Column(UnicodeText)
    wheelchair = Column(IntEnum(WheelchairAccess))
    email = Column(UnicodeText)
    roof_shape = Column(IntEnum(RoofShape))
    roof_colour = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
