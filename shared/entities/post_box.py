from . import OSMEntity

class PostBox(OSMEntity):
    collection_times: str = None
    operator: str = None
    drive_through: bool = None
    name: str = None
    level: int = None
    note: str = None