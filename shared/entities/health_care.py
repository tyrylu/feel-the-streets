import enum
from .building import Building

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
    type: HealthCareType
    speciality: HealthCareSpeciality = None