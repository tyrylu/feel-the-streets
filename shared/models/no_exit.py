from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class NoExit(Entity):
    __tablename__ = "no_exits"
    __mapper_args__ = {'polymorphic_identity': 'no_exit', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    fixme = Column(UnicodeText)
    note = Column(UnicodeText)
    todo = Column(UnicodeText)
    operator = Column(UnicodeText)
