from pydantic import BaseModel

class Bookmark(BaseModel):
    __tablename__ = "bookmarks"
    id: int
    area: int
    name: str
    latitude: float
    longitude: float
    direction: float