import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class CollectionType(enum.Enum):
    collection = 0
class Collection(Named):
    __tablename__ = "collections"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'collection'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(CollectionType))
    note = Column(UnicodeText)
    website = Column(UnicodeText)