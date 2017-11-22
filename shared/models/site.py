import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from . import Named
from .enums import OSMObjectType

class SiteType(enum.Enum):
    site = 0

class Site(Named):
    __tablename__ = "sites"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'site'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(SiteType))
    website = Column(UnicodeText)