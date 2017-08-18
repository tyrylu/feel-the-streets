from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from .entity import Entity

class Piste(Entity):
    __tablename__ = "pistes"
    __mapper_args__ = {'polymorphic_identity': 'piste'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(UnicodeText)
    difficulty = Column(UnicodeText)