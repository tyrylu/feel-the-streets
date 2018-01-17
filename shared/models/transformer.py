import enum
from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .power import Power
from .enums import OSMObjectType, TransformerType, PowerSubstationType

class Transformer(Power):
    __tablename__ = "transformers"
    __mapper_args__ = {'polymorphic_identity': 'transformer', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("powers.id"), primary_key=True)
    transformer_type = Column(IntEnum(TransformerType))
    phases = Column(Integer)
    rating = Column(UnicodeText)
    substation = Column(IntEnum(PowerSubstationType))

