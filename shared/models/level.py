from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, IndoorType

class Level(Named):
    __tablename__ = "levels"
    __mapper_args__ = {'polymorphic_identity': 'level', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    level = Column(Integer)
    indoor = Column(IntEnum(IndoorType))
