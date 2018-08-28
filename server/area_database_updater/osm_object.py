from pydantic import BaseModel
from typing import Dict, List
from shared.entities.enums import OSMObjectType

class OSMRelationMember(BaseModel):
    type: OSMObjectType
    ref: int
    role: str

    @property
    def unique_ref(self):
        return "{0}{1}".format(self.type.name[0], self.ref)
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

    @property
    def unique_id(self):
            return "{0}{1}".format(self.type.name[0], self.id)