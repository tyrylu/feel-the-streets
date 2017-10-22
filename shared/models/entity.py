from sqlalchemy import Column, String, DateTime, Integer
from ..sa_types import IntEnum
from geoalchemy import GeometryColumn, Geometry
from . import Base
from .enums import OSMObjectType, Role
import shapely.wkt as wkt

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    osm_type = Column(IntEnum(OSMObjectType), primary_key=True)
    version = Column(Integer, nullable=False)
    changeset = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    uid = Column(Integer, nullable=False)
    user = Column(String(256), nullable=False)
    parent_id = Column(Integer)
    parent_osm_type = Column(IntEnum(OSMObjectType))
    role = Column(IntEnum(Role))
    geometry = GeometryColumn(Geometry, nullable=False)
    discriminator = Column(String(64), nullable=False)
    __mapper_args__ = {'polymorphic_on': discriminator}
    
    def __str__(self):
        return self.__class__.__name__
    
    def get_shapely_geometry(self, db):
        return wkt.loads(db.scalar(self.geometry.wkt))