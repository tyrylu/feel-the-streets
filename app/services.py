import os
import sys
import platform
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .di import Singleton
from .sound_manager import SoundManager, SoundProperties
from .map import Map
from .config import Config
from .models import Base
from .speech_service import SpeechService
from .menu_service import MenuService

def create_app_db():
    db_path = os.path.join(config().config_path, "app.db")
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

speech = Singleton(SpeechService)
sound = Singleton(factory=create_sound)
map = Singleton(Map)
config = Singleton(factory=lambda: Config.from_user_config())
app_db_session = Singleton(factory=create_app_db)
menu_service = Singleton(MenuService)