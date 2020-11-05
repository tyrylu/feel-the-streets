import blinker
import enum

class MoveValidationResult(enum.Enum):
    reject = 0
    accept = 1
    cancel = 2

entity_pre_move = blinker.Signal()
entity_post_move = blinker.Signal()
entity_pre_enter = blinker.Signal()
entity_post_enter = blinker.Signal()
entity_pre_leave = blinker.Signal()
entity_post_leave = blinker.Signal()
entity_rotated = blinker.Signal()
entity_move_rejected = blinker.Signal()
from .entity import Entity
from .person import Person