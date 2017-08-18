import enum
from sqlalchemy import Column, Enum, ForeignKey, Integer
from . import Named

class AbandonedType(enum.Enum):
    path = 0

class Abandoned(Named):
    __tablename__ = "abandoned"
    __mapper_args__ = {'polymorphic_identity': 'abandoned'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(AbandonedType))
    