from sqlalchemy import Column, ForeignKey, Boolean, Integer
from .entity import Entity

class Fee(Entity):
    __tablename__ = "fees"
    __mapper_args__ = {'polymorphic_identity': 'fee'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    fee = Column(Boolean)