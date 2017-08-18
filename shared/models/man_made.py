import enum
from sqlalchemy import Column, ForeignKey, Boolean, Enum, Integer, UnicodeText
from .enums import ManMade
from . import Named

class SurveyllanceType(enum.Enum):
    none = 0
    public = 1


class ManMade(Named):
    __tablename__ = "man_made"
    __mapper_args__ = {'polymorphic_identity': 'man_made'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    type = Column(Enum(ManMade), nullable=False)
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
    surveillance = Column(Enum(SurveyllanceType))
    disused = Column(Boolean)
    start_date = Column(UnicodeText)