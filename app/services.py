import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import appdirs
from accessible_output2.outputs import auto
from .di import Singleton
from .sound_manager import SoundManager, SoundProperties
from .map import Map
from .config import Config
from .models import Base

def create_app_db():
    db_path = os.path.join(appdirs.user_data_dir("fts", appauthor=False, roaming=True), "app.db")
    engine = create_engine("sqlite:///{0}".format(db_path))
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    return session

def create_sound():
    if getattr(sys, "frozen", False):
        mgr = SoundManager(sounds_dir=os.path.join(sys._MEIPASS, "sounds"))
    else:
        mgr = SoundManager(sounds_dir=os.path.join(os.path.dirname(__file__), "sounds"))
    mgr.add_property_pattern("*", SoundProperties(is_3d=True, min_distance=1))
    return mgr

speech = Singleton(auto.Auto)
sound = Singleton(factory=create_sound)
map = Singleton(Map)
config = Singleton(Config)
app_db_session = Singleton(factory=create_app_db)