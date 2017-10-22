import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Annotated
from .enums import OSMObjectType

class NoticeCategory(enum.Enum):
    no_passage_left = 1
    no_passsage_right = 2

class NoticeFunction(enum.Enum):
    prohibition = 1

class NoticeImpact(enum.Enum):
    upstream = 1

class Notice(Annotated):
    __tablename__ = "notices"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["annotated.id", "annotated.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'notice'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    category = Column(IntEnum(NoticeCategory))
function = Column(IntEnum(NoticeFunction))
impact = Column(IntEnum(NoticeImpact))
orientation = Column(Integer)