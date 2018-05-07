from . import Named

class PostBox(Named):
    collection_times: str = None
    operator: str = None
    drive_through: bool = None
    level: int = None
    note: str = None