from sqlalchemy import Column, ForeignKey, Boolean, Integer
from .entity import Entity

class Bench(Entity):
    __tablename__ = "benches"
    __mapper_args__ = {'polymorphic_identity': 'bench'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    backrest = Column(Boolean)