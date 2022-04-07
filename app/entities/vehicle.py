from . import Entity
from ..services import sound

class Vehicle(Entity):
    speed: float = 0.0 # In km/h
    sound: str

    def __init__(self, **data):
        super().__init__(**data)
        x, y, z = self.cartesian_position
        self._sound_channel = sound().play(self.sound, x=x, y=y, z=z)
    
    def update_position(self, time_delta):
        meters_per_second = self.speed/3.6
        distance = meters_per_second*time_delta
        self.move_by(distance)
        x, y, z = self.cartesian_position
        self._sound_channel.position = (x, y, z)
        sound().fmodex_system.update()
