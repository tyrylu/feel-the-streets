import pydantic

class SoundProperties(pydantic.BaseModel):
    is_3d: bool
    min_distance: float