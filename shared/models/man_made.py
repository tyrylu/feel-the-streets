import enum
from sqlalchemy import Column, ForeignKeyConstraint, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum
from .enums import ManMade, OSMObjectType
from . import Named

class SurveyllanceType(enum.Enum):
    none = 0
    public = 1
    outdoor = 2
    indoor = 3
    webcam = 4
    

class ManMade(Named):
    __tablename__ = "man_made"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["named.id", "named.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'man_made'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(ManMade), nullable=False)
    classification = Column(UnicodeText)
    image = Column(UnicodeText)
    historic = Column(Boolean)
    network = Column(UnicodeText)
    layer = Column(Integer)
    location = Column(UnicodeText)
    substance = Column(UnicodeText)
    height = Column(Integer)
    handrail = Column(Boolean)
    email = Column(UnicodeText)
    website = Column(UnicodeText)
    telephone = Column(UnicodeText)
    operator = Column(UnicodeText)
    surveillance = Column(IntEnum(SurveyllanceType))
    disused = Column(Boolean)
    start_date = Column(UnicodeText)
    fixme = Column(UnicodeText)
    material = Column(UnicodeText)