from sqlalchemy import Column, Float, Integer
from . import Base

class IdxEntitiesGeometry(Base):
    __tablename__ = "idx_entities_geometry"
    pkid = Column(Integer, primary_key=True)
    xmin = Column(Float, nullable=False)
    xmax = Column(Float, nullable=False)
    ymin = Column(Float, nullable=False)
    ymax = Column(Float, nullable=False)
from . import Base