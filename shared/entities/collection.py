import enum
from . import Named

class CollectionType(enum.Enum):
    collection = 0

class Collection(Named):
    type: CollectionType = None
    note: str = None
    website: str = None
    wikidata: str = None
    description: str = None
    official_name: str = None
    wikipedia: str = None
    complete: bool = None
    fixme: str = None