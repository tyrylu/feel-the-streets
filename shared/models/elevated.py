from sqlalchemy import Column, ForeignKey, Integer, Float
from .entity import Entity

class Elevated(Entity):
    __tablename__ = "elevated"
    __mapper_args__ = {'polymorphic_identity': 'elevated'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    ele = Column(Float)