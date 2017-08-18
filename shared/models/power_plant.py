from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from . import Building

class PowerPlant(Building):
    __tablename__ = "power_plants"
    __mapper_args__ = {'polymorphic_identity': 'power_plant'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    electricity_output = Column(UnicodeText)
    frequency= Column(Integer)