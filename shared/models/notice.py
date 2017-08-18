import enum
from sqlalchemy import Column, Enum, ForeignKey, Integer, UnicodeText
from . import Annotated
class NoticeCategory(enum.Enum):
    no_passage_left = 1

class NoticeFunction(enum.Enum):
    prohibition = 1

class NoticeImpact(enum.Enum):
    upstream = 1

class Notice(Annotated):
    __tablename__ = "notices"
    __mapper_args__ = {'polymorphic_identity': 'notice'}
    id = Column(Integer, ForeignKey("annotated.id"), primary_key=True)
    category = Column(Enum(NoticeCategory))
function = Column(Enum(NoticeFunction))
impact = Column(Enum(NoticeImpact))
orientation = Column(Integer)
