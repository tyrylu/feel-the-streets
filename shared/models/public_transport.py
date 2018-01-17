from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from ..sa_types import IntEnum
from .named import Named
from .enums import OSMObjectType, SiteType

class PublicTransport(Named):
    __tablename__ = "public_transports"
    __mapper_args__ = {'polymorphic_identity': 'public_transport', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    network = Column(UnicodeText)
    pub = Column(IntEnum(SiteType))
