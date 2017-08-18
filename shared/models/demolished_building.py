from sqlalchemy import Column, ForeignKey, Integer
from .entity import Entity

class DemolishedBuilding(Entity):
    __tablename__ = "demolished_buildings"
    __mapper_args__ = {'polymorphic_identity': 'demolished_building'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    