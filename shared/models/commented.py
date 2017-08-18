from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from .entity import Entity

class Commented(Entity):
    __tablename__ = "commented"
    __mapper_args__ = {'polymorphic_identity': 'commented'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    comment = Column(UnicodeText())