import enum
from sqlalchemy import Column, ForeignKey, Boolean, Integer, UnicodeText
from ..sa_types import IntEnum, DimensionalFloat
from .enums import ManMade, OSMObjectType, SurveillanceType, AccessType, Material
from .enums import ManMade, OSMObjectType, SurveillanceType, AccessType, Material
from . import Named

class PumpType(enum.Enum):
    manual = 0

class StreetCabinetType(enum.Enum):
    power = 0

class PipelineType(enum.Enum):
    water = 0

class ManMade(Named):
    __tablename__ = "man_made"
    __mapper_args__ = {'polymorphic_identity': 'man_made', 'polymorphic_load': 'selectin'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(IntEnum(ManMade), nullable=False)
    classification = Column(UnicodeText)
    image = Column(UnicodeText)
    historic = Column(Boolean)
    network = Column(UnicodeText)
    layer = Column(Integer)
    location = Column(UnicodeText)
    substance = Column(UnicodeText)
    height = Column(DimensionalFloat("meter"))
    handrail = Column(Boolean)
    email = Column(UnicodeText)
    website = Column(UnicodeText)
    telephone = Column(UnicodeText)
    operator = Column(UnicodeText)
    surveillance = Column(IntEnum(SurveillanceType))
    disused = Column(Boolean)
    start_date = Column(UnicodeText)
    fixme = Column(UnicodeText)
    material = Column(IntEnum(Material))
    bridge = Column(Boolean)
    pipeline = Column(IntEnum(PipelineType))
    # Separate entity?
    tunnel = Column(Boolean)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)
    access = Column(IntEnum(AccessType))
    pump = Column(IntEnum(PumpType))
    # Separate entity?
    street_cabinet = Column(IntEnum(StreetCabinetType))
    # Separate entity?
    count = Column(Integer)
    usage = Column(UnicodeText)
    # Probably have something in common
    floating = Column(Boolean)
    note = Column(UnicodeText)
    wifi_ssid = Column(UnicodeText)
    building_material = Column(IntEnum(Material))
    sorting_name = Column(UnicodeText)
    loc_name = Column(UnicodeText)
    voltage = Column(Integer)
    note_en = Column(UnicodeText)
    air_quality_monitoring = Column(Boolean)
    description = Column(UnicodeText)
