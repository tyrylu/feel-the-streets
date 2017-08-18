import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from . import Tourism

class BoardType(enum.Enum):
    none = 0
    history = 1
    history_technology = 2
    nature = 3
    wildlife = 4
    geology = 5
    agriculture= 6
    technology = 7

class Board(Tourism):
    __tablename__ = "boards"
    __mapper_args__ = {'polymorphic_identity': 'board'}
    id = Column(Integer, ForeignKey("tourisms.id"), primary_key=True)
    board_type = Column(Enum(BoardType))
    board_number = Column(Integer)