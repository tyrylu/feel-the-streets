from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import AccessType, OSMObjectType

class Accessible(Entity):
    __tablename__ = "accessibles"
    __mapper_args__ = {'polymorphic_identity': 'accessible', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(AccessType), nullable=False)
    level = Column(UnicodeText)
    door = Column(IntEnum(AccessType))
