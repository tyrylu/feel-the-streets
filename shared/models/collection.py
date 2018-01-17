import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class CollectionType(enum.Enum):
    collection = 0

class Collection(Named):
    __tablename__ = "collections"
    __mapper_args__ = {'polymorphic_identity': 'collection', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(CollectionType))
    note = Column(UnicodeText)
    website = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    description = Column(UnicodeText)
    official_name = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    complete = Column(Boolean)
    fixme = Column(UnicodeText)
