import enum
from sqlalchemy import Column, ForeignKey, Integer
from ..sa_types import IntEnum
from .entity import Entity
from .enums import OSMObjectType

class SchoolRelatedThingType(enum.Enum):
    entrance = 0

class SchoolThing(Entity):
    __tablename__ = "school_things"
    __mapper_args__ = {'polymorphic_identity': 'school_thing', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(IntEnum(SchoolRelatedThingType))