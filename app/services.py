import os
from .di import Singleton
from accessible_output2.outputs import auto
from .sound_manager import SoundManager, SoundProperties
from .map import Map

def create_sound():
    mgr = SoundManager(sounds_dir=os.path.join(os.path.dirname(__file__), "sounds"))
    mgr.add_property_pattern("*", SoundProperties(is_3d=True, min_distance=1))
    return mgr

speech = Singleton(auto.Auto)
sound = Singleton(factory=create_sound)
map = Singleton(Map)