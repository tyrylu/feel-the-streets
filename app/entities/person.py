from . import Entity
from ..services import config

class Person(Entity):
    use_step_sounds = True

    def move_to_current(self):
        self.move_to(self.position)

    def step_forward(self):
        self.move_by(config().navigation.step_length)
    
    def step_backward(self):
        self.move_by(-config().navigation.step_length)
    