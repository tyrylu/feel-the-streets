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


    @classmethod
    def from_xml(cls, element: Element):
        action = cls.parse_obj(element.attrib)
        if action.type is OSMChangeType.create:
            action.new = OSMObject.from_xml(element.getchildren()[0])
        elif action.type is OSMChangeType.modify:
            action.old = OSMObject.from_xml(element.find("old").getchildren()[0])
            action.new = OSMObject.from_xml(element.find("new").getchildren()[0])
        elif action.type is OSMChangeType.delete:
            action.old = OSMObject.from_xml(element.find("old").getchildren()[0])
        return action
