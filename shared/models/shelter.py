import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer, UnicodeText
from ..sa_types import IntEnum
from .entity import Entity
from .enums import BuildingType, OSMObjectType, TourismType

class ShelterType(enum.Enum):
    unknown = 0
    public_transport = 1
    picnic_shelter = 2
    wather_shelter = 3
    weather_shelter = 6
    wildlife_hide = 7
    
    

class Shelter(Entity):
    __tablename__ = "shelters"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["entities.id", "entities.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'shelter'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(ShelterType))
    building = Column(IntEnum(BuildingType))
    tourism = Column(IntEnum(TourismType))
    bench = Column(UnicodeText)