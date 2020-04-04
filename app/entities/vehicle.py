import attr
from anglr import Angle
from . import Entity
from ..services import sound

@attr.s
class Vehicle(Entity):
    speed = attr.ib(default=0) # In km/h
    sound = attr.ib()

    def __attrs_post_init__(self):
        x, y, z = self.cartesian_position
        self._sound_channel = sound().play(self.sound, x=x, y=y, z=z)
    
   
    def update_position(self, time_delta):
        meters_per_second = self.speed/3.6
        distance = meters_per_second*time_delta
        self.move_by(distance)
        x, y, z = self.cartesian_position
        self._sound_channel.position = (x, y, z)
        sound().fmodex_system.update()
