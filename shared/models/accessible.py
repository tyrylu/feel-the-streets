from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity
from .enums import AccessType


class Accessible(Entity):
    __tablename__ = "accessibles"
    __mapper_args__ = {'polymorphic_identity': 'accessible'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(AccessType), nullable=False)