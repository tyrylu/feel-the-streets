from .power import Power
from .enums import TransformerType, PowerSubstationType

class Transformer(Power):
    transformer_type: TransformerType = None
    phases: int = None
    rating: str = None
    substation: PowerSubstationType = None
