from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, SiteType

class Street(Named):
    __tablename__ = "streets"
    __mapper_args__ = {'polymorphic_identity': 'street', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    site = Column(IntEnum(SiteType))
