import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from sqlalchemy.orm import relationship
from .enums import ShopType, ManMade, BarrierType, NaturalType, LeisureType, LandType
from . import Named

class MeadowType(enum.Enum):
    none = 0
    agricultural = 1

class MilitaryType(enum.Enum):
    none = 0
    barracks = 1

class Land(Named):
    __tablename__ = "lands"
    __mapper_args__ = {'polymorphic_identity': 'land'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(LandType), nullable=False)
    shop_type = Column(Enum(ShopType))
    website = Column(UnicodeText)
    meadow_type = Column(Enum(MeadowType))
    man_made = Column(Enum(ManMade))
    crop = Column(UnicodeText)
    barrier = Column(Enum(BarrierType))
    note = Column(UnicodeText)
    comment = Column(UnicodeText)
    natural_type = Column(Enum(NaturalType))
    military_type = Column(Enum(MilitaryType))
    operator = Column(UnicodeText)
    resource = Column(UnicodeText)
    leisure = Column(Enum(LeisureType))
    address_id = Column(Integer, ForeignKey("addresses.id"))
    address = relationship("Address")
    leaf_cycle = Column(UnicodeText)
    religion = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
