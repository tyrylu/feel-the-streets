from sqlalchemy import Column, String, Integer
from geoalchemy import GeometryColumn, Geometry
from . import Base
import shapely.wkt as wkt

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    geometry = GeometryColumn(Geometry, nullable=False)
    discriminator = Column(String(64), nullable=False)
    __mapper_args__ = {'polymorphic_on': discriminator}
    
    def __str__(self):
        return self.__class__.__name__
    
    def get_shapely_geometry(self, db):
        return wkt.loads(db.scalar(self.geometry.wkt))