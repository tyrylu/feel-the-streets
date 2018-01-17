import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType, BuildingType, Location, Material, PowerType

class Power(Entity):
    __tablename__ = "powers"
    __mapper_args__ = {'polymorphic_identity': 'power', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(PowerType), nullable=False)
    building = Column(IntEnum(BuildingType))
    layer = Column(Integer)
    fixme = Column(UnicodeText)
    location = Column(IntEnum(Location))
    high_voltage = Column(Integer)
    voltage = Column(Integer)
    low_voltage = Column(Integer)
    material = Column(IntEnum(Material))
    transition_location = Column(Boolean)
    tower = Column(IntEnum(PowerType))
    frequency = Column(Integer)
    area = Column(Boolean)
    operator = Column(UnicodeText)
