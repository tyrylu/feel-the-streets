from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from .entity import Entity

class PostBox(Entity):
    __tablename__ = "post_boxes"
    __mapper_args__ = {'polymorphic_identity': 'post_box'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    collection_times = Column(UnicodeText)
    operator = Column(UnicodeText)