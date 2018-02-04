import enum
from .enums import ManMade, SurveillanceType, AccessType, Material
from . import Named
from ..validated_quantity import quantity

class PumpType(enum.Enum):
    manual = 0

class StreetCabinetType(enum.Enum):
    power = 0

class PipelineType(enum.Enum):
    water = 0

class ManMade(Named):
    type: ManMade
    classification: str = None
    image: str = None
    historic: bool = None
    network: str = None
    layer: int = None
    location: str = None
    substance: str = None
    height: quantity("meter") = None
    handrail: bool = None
    email: str = None
    website: str = None
    telephone: str = None
    operator: str = None
    surveillance: SurveillanceType = None
    disused: bool = None
    start_date: str = None
    fixme: str = None
    material: Material = None
    bridge: bool = None
    pipeline: PipelineType = None
    # Separate entity?
    tunnel: bool = None
    wikidata: str = None
    wikipedia: str = None
    access: AccessType = None
    pump: PumpType = None
    # Separate entity?
    street_cabinet: StreetCabinetType = None
    # Separate entity?
    count: int = None
    usage: str = None
    # Probably have something in common
    floating: bool = None
    note: str = None
    wifi_ssid: str = None
    building_material: Material = None
    sorting_name: str = None
    loc_name: str = None
    voltage: int = None
    note_en: str = None
    air_quality_monitoring: bool = None
    description: str = None