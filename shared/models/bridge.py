from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType

class Bridge(Named):
    __tablename__ = "bridges"
    __mapper_args__ = {'polymorphic_identity': 'bridge', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    wikidata = Column(UnicodeText)
    sorting_name = Column(UnicodeText)
