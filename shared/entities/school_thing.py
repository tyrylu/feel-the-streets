import enum
from . import OSMEntity

class SchoolRelatedThingType(enum.Enum):
    entrance = 0

class SchoolThing(OSMEntity):
    type: SchoolRelatedThingType = None