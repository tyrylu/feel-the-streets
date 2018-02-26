from pydantic import BaseModel
from typing import Dict, List
from xml.etree.ElementTree import Element
from shared.entities.enums import OSMObjectType

class OSMRelationMember(BaseModel):
    type: OSMObjectType
    ref: int
    role: str

class OSMObject(BaseModel):
    id: int
    type: OSMObjectType
    timestamp: str
    version: int
    changeset: int
    user: str
    uid: int
    tags: Dict[str, str] = {}
    lat: float = None
    lon: float = None
    nodes: List[int] = None
    members: List[OSMRelationMember] = None

    @classmethod
    def from_dict(cls, element_data):
        return cls.parse_obj(element_data)

    @classmethod
    def from_xml(cls, element: Element):
        data = element.attrib.copy()
        data["type"] = element.tag
        tags = {}
        for tag in element.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]
        data["tags"] = tags
        nodes = []
        for node in element.findall("nd"):
            nodes.append(node.attrib["ref"])
        data["nodes"] = nodes
        members = []
        for member in element.findall("member"):
            members.append(OSMRelationMember.parse_obj(member.attrib))
        data["members"] = members
        return cls.parse_obj(data)

    @property
    def unique_id(self):
            return "{0}{1}".format(self.type.name[0], self.id)