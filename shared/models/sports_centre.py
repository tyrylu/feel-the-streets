from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from . import Building

class SportsCentre(Building):
    __tablename__ = "sport_centers"
    __mapper_args__ = {'polymorphic_identity': 'sport_center'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    int_name = Column(UnicodeText)