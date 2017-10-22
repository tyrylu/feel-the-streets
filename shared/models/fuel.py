from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from sqlalchemy.orm import relationship
from .enums import BuildingType, ShopType, OSMObjectType
from .entity import Entity

class Fuel(Entity):
    __tablename__ = "fuels"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'fuel'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
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