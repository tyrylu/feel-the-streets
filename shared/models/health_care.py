import enum
from sqlalchemy import Column, ForeignKeyConstraint, Integer
from ..sa_types import IntEnum
from .building import Building
from .enums import OSMObjectType

class HealthCareType(enum.Enum):
    hospital = 0
    doctor = 1
    optometrist = 2
    psychotherapist = 3
    physiotherapist = 4
    dentist = 5

class HealthCareSpeciality(enum.Enum):
    paediatrics = 0
    emergency = 1
    gynaecology = 2
    otolaryngology = 3
    psychiatry = 4
    general = 5
    neurology = 6
    internal = 7
    vascular_surgery = 8
    orthopaedics = 9
    

class HealthCare(Building):
    __tablename__ = "healthcares"
    __table_args__ = (ForeignKeyConstraint(["id", "osm_type"], ["buildings.id", "buildings.osm_type"]),)
    __mapper_args__ = {'polymorphic_identity': 'healthcare'}
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    type = Column(IntEnum(HealthCareType), nullable=False)
    speciality = Column(IntEnum(HealthCareSpeciality)) # Make it a list