import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from .power import Power
from .enums import OSMObjectType

class TransformerType(enum.Enum):
    distribution = 0
    traction = 1

class Transformer(Power):
    __tablename__ = "transformers"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["powers.id", "powers.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'transformer'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    transformer_type = Column(IntEnum(TransformerType))
    operator = Column(UnicodeText)
    frequency = Column(Integer)
    phases = Column(Integer)
    rating = Column(UnicodeText)
    