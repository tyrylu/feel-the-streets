import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from . import Tourism
from .enums import OSMObjectType

class BoardType(enum.Enum):
    none = 0
    history = 1
    history_technology = 2
    nature = 3
    wildlife = 4
    geology = 5
    agriculture= 6
    technology = 7
    notice = 8
    board = 9
    history_nature = 10
    plants = 11
    map = 12
    coast_guard = 13
    nature_history = 14
    quiz = 15
    tree = 16
    sport = 17
    historic = 18
    timetable = 19
    transport = 20

   
class Board(Tourism):
    __tablename__ = "boards"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["tourisms.id", "tourisms.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'board'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    board_type = Column(IntEnum(BoardType))
    board_number = Column(Integer)
    board_ref = Column(Integer)
    