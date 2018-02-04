from . import Named
from .enums import TourismType, TransformerType, PowerType, InfoType

class Pole(Named):
    transformer_type: TransformerType = None
    voltage: str = None
    operator: str = None
    note: str = None
    fixme: str = None
    hiking: bool = None
    tourism: TourismType = None
    pole: PowerType = None
    disused: bool = None
    ele: int = None
    information: InfoType = None