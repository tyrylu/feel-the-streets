from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from . import Building

class Castle(Building):
    __tablename__ = "castles"
    __mapper_args__ = {'polymorphic_identity': 'castle'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    type = Column(UnicodeText)