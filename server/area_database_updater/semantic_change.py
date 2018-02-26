import enum
from typing import List
from pydantic import BaseModel
from .diff_utils import DictChange

class ChangeType(enum.Enum):
    create = 0
    update = 1
    delete = 2

class Change(BaseModel):
    osm_id: str
    type: ChangeType
    property_changes: List[DictChange] = []
    data_changes: List[DictChange] = []