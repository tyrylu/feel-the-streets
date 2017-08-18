import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity
from .enums import BuildingType

class ShelterType(enum.Enum):
    unknown = 0
    public_transport = 1

class Shelter(Entity):
    __tablename__ = "shelters"
    __mapper_args__ = {'polymorphic_identity': 'shelter'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(ShelterType))
    building = Column(Enum(BuildingType))