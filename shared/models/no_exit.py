from sqlalchemy import Column, ForeignKey, Integer
from .entity import Entity

class NoExit(Entity):
    __tablename__ = "no_exits"
    __mapper_args__ = {'polymorphic_identity': 'no_exit'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
        