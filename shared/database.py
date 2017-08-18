import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from geoalchemy import GeometryDDL
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

    def _post_connect(self,dbapi_connection, connection_record):
        dbapi_connection.enable_load_extension(True)
        dbapi_connection.load_extension("mod_spatialite")
        if self._creating: 
            log.debug("Initializing spatial metadata...")
            dbapi_connection.execute("SELECT InitSpatialMetadata(1)")

    def create(self):
        self._creating = True
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