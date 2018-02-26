from collections import defaultdict
import os
import logging
from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from geoalchemy import GeometryDDL, Geometry
from .models import Base, Entity, IdxEntitiesGeometry, Bookmark
from . import sqlalchemy_logging

log = logging.getLogger(__name__)
os.environ["PATH"] = r"C:\users\lukas\apps;%s"%os.environ["PATH"]

class Database:
    @classmethod
    def get_database_storage_root(cls):
        root = "databases"
        if not os.path.exists(root):
            os.makedirs(root)
        return root
    @classmethod
    def get_database_file(cls, area_name):
        return os.path.join(cls.get_database_storage_root(), "%s.db"%area_name)
    
    def __init__(self, area_name):
        db_path = self.get_database_file(area_name)
        self._creating = False
        self._engine = create_engine("sqlite:///%s"%db_path)
        event.listen(self._engine, "connect", self._post_connect)
        self._session = sessionmaker(bind=self._engine)()
        self._per_table_values = defaultdict(list)
        self._foreign_ids = defaultdict(lambda: 1)
        
    def _post_connect(self, dbapi_connection, connection_record):
        dbapi_connection.enable_load_extension(True)
        dbapi_connection.load_extension("mod_spatialite")
        if self._creating: 
            log.debug("Initializing spatial metadata...")
            dbapi_connection.execute("SELECT InitSpatialMetadata(1)")

    def create_if_needed(self):
        self._creating = not self._engine.dialect.has_table(self._engine, "entities")
        if self._creating:
            log.debug("Running geometry DDL...")
            GeometryDDL(Entity.__table__)
            log.debug("Creating database tables...")
            Entity.__table__.create(self._engine)
            Bookmark.__table__.create(self._engine)
            self._creating = False

    def add(self, instance):
        self._session.add(instance)

    def commit(self):
        self._session.commit()
    
    def merge(self, entity):
        self._session.merge(entity)
    
    def query(self, *entities, **kwargs):
        return self._session.query(*entities, **kwargs)

    def scalar(self, *args, **kwargs):
        return self._session.scalar(*args, **kwargs)

    @property
    def bounds(self):
        min = func.min
        max = func.max
        return self._session.query(min(IdxEntitiesGeometry.xmin), max(IdxEntitiesGeometry.xmax), min(IdxEntitiesGeometry.ymin), max(IdxEntitiesGeometry.ymax)).one()

    @property
    def last_timestamp(self):
        max = func.max
        json_extract = func.json_extract
        return self.scalar(max(json_extract(Entity.data, "$.timestamp")))
    
    def schedule_entity_addition(self, entity):
        per_table_values = defaultdict(dict)
        self._set_foreign_keys(entity)
        for table in inspect(entity.__class__).tables:
            for column in table.columns.values():
                value = getattr(entity, column.name)
                # Manual override for geometry columns
                if isinstance(column.type, Geometry) and value is not None:
                    value = value.desc
                per_table_values[column.table][column.name] = value
        for table, row in per_table_values.items():
            self._per_table_values[table].append(row)

    def _set_foreign_keys(self, entity):
        """Foreign key generation and other related functionality."""
        for table in inspect(entity.__class__).tables:
            for column in table.columns.values():
                if column.name.endswith("_id") and column.foreign_keys:
                    value_attr = column.name[:-3]
                    foreign_value = getattr(entity, value_attr)
                    if foreign_value:
                        foreign_id = self._set_foreign_id(foreign_value)
                        setattr(entity, column.name, foreign_id)
                        self.schedule_entity_addition(foreign_value)

    def _set_foreign_id(self, foreign_entity):
        table = foreign_entity.__tablename__
        free_id = self._foreign_ids[table]
        self._foreign_ids[table] += 1
        foreign_entity.id = free_id
        return free_id
    def add_entities(self):
        with self._engine.begin() as conn:
            conn.execute("pragma synchronous=off")
            for table, rows in self._per_table_values.items():
                values_dict = {}
                for col in table.columns.values():
                    if isinstance(col.type, Geometry):
                        values_dict[col.name] = text("GeomFromText(:%s, 4326)"%col.name)
                    else:
                        values_dict[col.name] = ":%s"%col.name
                stmt = table.insert().values(values_dict)
                log.info("Adding %s rows to the %s table.", len(rows), table.name)
                length = len(rows)
                chunk_size = 10000
                for i in range(0, length, chunk_size):
                    log.info("Inserting rows from index %s.", i)
                    conn.execute(stmt, rows[i:i+chunk_size])


    def has_entity(self, osm_id):
            return self.query(Entity).filter(func.json_extract(Entity.data, "$.osm_id") == osm_id).count() == 1

    def get_entity_by_osm_id(self, osm_id):
        return self.query(Entity).filter(func.json_extract(Entity.data, "$.osm_id") == osm_id).one_or_none()