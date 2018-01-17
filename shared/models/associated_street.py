from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType

class AssociatedStreet(Named):
    __tablename__ = "associated_streets"
    __mapper_args__ = {'polymorphic_identity': 'associated_street', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
