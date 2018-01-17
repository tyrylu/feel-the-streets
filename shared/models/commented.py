from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Commented(Entity):
    __tablename__ = "commented"
    __mapper_args__ = {'polymorphic_identity': 'commented', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    comment = Column(UnicodeText())
