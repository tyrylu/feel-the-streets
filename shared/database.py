import collections
import os
import logging
from sqlalchemy import create_engine, event, text, inspect
from sqlalchemy.orm import sessionmaker
from geoalchemy import GeometryDDL, Geometry
from .models import Base, Entity


log = logging.getLogger(__name__)
os.environ["PATH"] = r"C:\users\lukas\apps;%s"%os.environ["PATH"]

class Database:
    def __init__(self, area_name):
        db_path = "%s.db"%area_name
        self._creating = False
        self._engine = create_engine("sqlite:///%s"%db_path)
        event.listen(self._engine, "connect", self._post_connect)
        self._session = sessionmaker(bind=self._engine)()
        self._per_table_values = collections.defaultdict(list)
        self._bind_processors = {}
        

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
            Base.metadata.create_all(self._engine)
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

    def merge(self, entity):
        return self._session.merge(entity)

    def schedule_entity_addition(self, entity):
        per_table_values = collections.defaultdict(dict)
        for table in inspect(entity.__class__).tables:
            for column in table.columns.values():
                #processor = self._lookup_bind_processor(column.type)
                value = getattr(entity, column.name)
                # Manual override for geometry columns
                if isinstance(column.type, Geometry) and value is not None:
                    value = value.desc
                per_table_values[column.table][column.name] = value
        for table, row in per_table_values.items():
            self._per_table_values[table].append(row)
    
    def _lookup_bind_processor(self, sa_type):
        if not sa_type in self._bind_processors:
            self._bind_processors[sa_type] = sa_type.bind_processor(self._engine.dialect)
        return self._bind_processors[sa_type]
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
