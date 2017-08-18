import enum
from sqlalchemy import Column, ForeignKey, Integer, Enum
from .entity import Entity

class AdvertisingType(enum.Enum):
    column = 0

class Advertising(Entity):
    __tablename__ = "advertisings"
    __mapper_args__ = {'polymorphic_identity': 'advertising'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(AdvertisingType), nullable=False)
    height = Column(Integer)