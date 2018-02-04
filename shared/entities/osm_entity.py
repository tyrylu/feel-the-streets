from pydantic import BaseModel
from .enums import OSMObjectType
from ..models import Entity

class OSMEntity(BaseModel):
    osm_id: int
    osm_type: OSMObjectType
    version: int
    changeset: int
    uid: int
    user: str
    parent_osm_id: int = None
    parent_osm_type: OSMObjectType = None
    db_entity: Entity = None # Newer will be, but it allows the property processing logic to pass.

    class Config:
        allow_mutation = False
    
    def __hash__(self):
        return hash(repr(self))
    def __str__(self):
        return self.__class__.__name__