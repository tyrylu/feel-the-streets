import os
import sys
import platform
from .di import Singleton
from .sound_manager import SoundManager, SoundProperties
from .map import Map
from .config import Config
from .speech_service import SpeechService
from .menu_service import MenuService
from .app_db import AppDb

def create_app_db():
    db_path = os.path.join(config().config_path, "app.db")
    return AppDb(db_path)

def create_sound():
    if getattr(sys, "frozen", False):
        sounds_dir = os.path.join(sys._MEIPASS, "sounds")
    else:
        sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
    x, y = map().project_latlon(map().default_start_location)
    mgr = SoundManager(sounds_dir=sounds_dir, init_hrtf=config().sounds.enable_hrtf, coordinates_divider=10, coordinate_decimal_places=2, origin=(x, y, 0))
    mgr.add_property_pattern("*", SoundProperties(is_3d=True, min_distance=1))
    return mgr

speech = Singleton(SpeechService)
sound = Singleton(factory=create_sound)
map = Singleton(Map)
config = Singleton(factory=lambda: Config.from_user_config())
app_db = Singleton(factory=create_app_db)
menu_service = Singleton(MenuService)