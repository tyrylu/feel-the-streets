import enum
from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from .entity import Entity

class TransformerType(enum.Enum):
    distribution = 0

class Pole(Entity):
    __tablename__ = "poles"
    __mapper_args__ = {'polymorphic_identity': 'pole'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    transformer_type = Column(Enum(TransformerType))
    voltage = Column(UnicodeText)