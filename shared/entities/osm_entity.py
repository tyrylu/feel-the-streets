import json
import datetime
from pydantic import BaseModel
from .enums import OSMObjectType
from ..models import Entity

class OSMEntity(BaseModel):
    osm_id: int
    osm_type: OSMObjectType
    timestamp: datetime.datetime
    version: int
    changeset: int
    uid: int
    user: str
    parent_osm_id: int = None
    parent_osm_type: OSMObjectType = None
    db_entity: Entity = None # Newer will be, but it allows the property processing logic to continue without marking all entities as missing a crucial property.

    class Config:
        allow_mutation = False
    
    def __hash__(self):
        return hash(repr(self))
    def __str__(self):
        return self.__class__.__name__

    @property
    def additional_fields(self):
        names = set(self.__fields__.keys())
        props = json.loads(self.db_entity.data)
        unknown_props = {key: val for key, val in props.items() if key not in names}
        return unknown_props
