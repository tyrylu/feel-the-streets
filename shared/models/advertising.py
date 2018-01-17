import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType, AdvertisingType

class Advertising(Entity):
    __tablename__ = "advertisings"
    __mapper_args__ = {'polymorphic_identity': 'advertising', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(AdvertisingType), nullable=False)
    height = Column(Integer)
    lit = Column(Boolean)
    direction = Column(Integer)
    name = Column(UnicodeText)
