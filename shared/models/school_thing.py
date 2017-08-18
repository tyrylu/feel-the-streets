import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer
from .entity import Entity

class SchoolRelatedThingType(enum.Enum):
    entrance = 0

class SchoolThing(Entity):
    __tablename__ = "school_things"
    __mapper_args__ = {'polymorphic_identity': 'school_thing'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(SchoolRelatedThingType))