from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class PostBox(Entity):
    __tablename__ = "post_boxes"
    __mapper_args__ = {'polymorphic_identity': 'post_box', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    collection_times = Column(UnicodeText)
    operator = Column(UnicodeText)
    drive_through = Column(Boolean)
    name = Column(UnicodeText)
    level = Column(Integer)
    note = Column(UnicodeText)
