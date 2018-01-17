from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class Piste(Entity):
    __tablename__ = "pistes"
    __mapper_args__ = {'polymorphic_identity': 'piste', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(UnicodeText)
    difficulty = Column(UnicodeText)