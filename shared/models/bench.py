from sqlalchemy import Column, ForeignKey, Boolean, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Bench(Entity):
    __tablename__ = "benches"
    __mapper_args__ = {'polymorphic_identity': 'bench', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    backrest = Column(Boolean)