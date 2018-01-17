import enum
from sqlalchemy import Column, ForeignKey, Integer
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
    __mapper_args__ = {'polymorphic_identity': 'healthcare', 'polymorphic_load': 'inline'}
    id = Column(Integer, ForeignKey("buildings.id"), primary_key=True)
    type = Column(IntEnum(HealthCareType), nullable=False)
    speciality = Column(IntEnum(HealthCareSpeciality)) # Make it a list