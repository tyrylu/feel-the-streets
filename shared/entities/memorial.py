from . import Historic
from .enums import MemorialKind

class Memorial(Historic):
    memorial_kind: MemorialKind = None
    url: str = None
    text: str = None
    network: str = None
    # Make it a date in a later pass
    person_date_of_death: str = None
    wikipedia_en: str = None
    level: int = None
    inscription_cs: str = None
    fixme: str = None