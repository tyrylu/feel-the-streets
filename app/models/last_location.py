from pydantic import BaseModel

class LastLocation(BaseModel):
    id: int
    area: str
    latitude: float
    longitude: float
    direction: float