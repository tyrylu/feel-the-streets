import enum
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
    yes = 21
    architeture = 22

class Board(Tourism):
    board_type: BoardType = None
    board_number: int = None
    board_ref: int = None
    education: bool = None
    language_cs: bool = None
