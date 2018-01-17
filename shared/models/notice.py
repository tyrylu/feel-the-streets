import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Annotated
from .enums import OSMObjectType, NoticeImpact,  NoticeFunction, NoticeType, NoticeCategory

class Notice(Annotated):
    __tablename__ = "notices"
    __mapper_args__ = {'polymorphic_identity': 'notice', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("annotated.id"), primary_key=True)
    category = Column(IntEnum(NoticeCategory))
    function = Column(IntEnum(NoticeFunction))
    impact = Column(IntEnum(NoticeImpact))
    orientation = Column(Integer)
    type = Column(IntEnum(NoticeType))
