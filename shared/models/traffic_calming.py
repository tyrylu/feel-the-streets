from sqlalchemy import Column, ForeignKey, Enum, Integer, UnicodeText
from .enums import TrafficCalmingType
from .entity import Entity

class TrafficCalming(Entity):
    __tablename__ = "traffic_calmings"
    __mapper_args__ = {'polymorphic_identity': 'traffic_calming'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    type = Column(Enum(TrafficCalmingType), nullable=False)
    note = Column(UnicodeText)