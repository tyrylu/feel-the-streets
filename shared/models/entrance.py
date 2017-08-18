import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Named

class EntranceType(enum.Enum):
    main = 0
    yes = 1

class Entrance(Named):
    __tablename__ = "entrances"
    __mapper_args__ = {'polymorphic_identity': 'entrance'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(EntranceType), nullable=False)