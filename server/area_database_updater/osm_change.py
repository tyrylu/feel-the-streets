import enum
from xml.etree.ElementTree import Element
from pydantic import BaseModel
from .osm_object import OSMObject

class OSMChangeType(enum.Enum):
    create = "create"
    modify = "modify"
    delete = "delete"

class OSMObjectChange(BaseModel):
    type: OSMChangeType
    old: OSMObject = None
    new: OSMObject = None
