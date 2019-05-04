import json
from sqlalchemy import Column, Float, String, UnicodeText, Integer, Index, func, text
from geoalchemy import GeometryColumn, Geometry
from . import Base
import shapely.wkt as wkt
from ..services import entity_registry

class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True)
    geometry = GeometryColumn(Geometry, nullable=False)
    discriminator = Column(String(64), nullable=False)
    data = Column(UnicodeText, nullable=False)
    effective_width = Column(Float)
    __table_args__ = (Index("entity_by_osm_id", func.json_extract(data, "$.osm_id")),)

    def __str__(self):
        return self.__class__.__name__
    
    def get_shapely_geometry(self, db):
        return wkt.loads(db.scalar(self.geometry.wkt))

    def create_osm_entity(self):
        entity_attrs = json.loads(self.data)
        entity_attrs["db_entity"] = self
        print(f"Creating {self.discriminator} from {entity_attrs}")
        return entity_registry().lookup_entity_class_by_discriminator(self.discriminator).parse_obj(entity_attrs)
     
    @classmethod
    def get_validators(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, val):
        if not isinstance(val, Entity):
            raise TypeError("Not an entity subclass.")
        return val