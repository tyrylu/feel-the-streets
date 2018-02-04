from . import Named
from .enums import IndoorType

class Level(Named):
    level: int = None
    indoor: IndoorType = None