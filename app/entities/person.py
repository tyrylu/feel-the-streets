import attr
import faker
from . import entity_pre_move, entity_post_move, entity_pre_enter, entity_post_enter, entity_pre_leave, entity_post_leave, entity_rotated
from shapely.geometry.point import Point
from ..measuring import measure

@attr.s(hash=True)
class Person:
    STEP_LENGTH = 0.7874 # Meters
    map = attr.ib(hash=False)
    position = attr.ib(hash=False)
    direction = attr.ib(default=0, hash=False)
    name = attr.ib(default=attr.Factory(faker.Faker().name))
    is_inside_of = attr.ib(default=attr.Factory(set), hash=False)
    def move_to_current(self):
        self.move_to(self.position)

    def move_to(self, pos):
        if entity_pre_move.has_receivers_for(self):
            for func, ret in entity_pre_move.send(self, new_pos=pos):
                if not ret:
                    return False
        with measure("Inside of query"):
            new_inside_of = set(self.map.intersections_at_position(pos))
        if entity_pre_enter.has_receivers_for(self) or entity_post_enter.has_receivers_for(self):
            enters = new_inside_of.difference(self.is_inside_of)
        if entity_pre_enter.has_receivers_for(self):
            for entered in enters:
                for func, ret in entity_pre_enter.send(self, enters=entered):
                    if not ret:
                        return False
        if entity_pre_leave.has_receivers_for(self) or entity_post_leave.has_receivers_for(self):
            leaves = self.is_inside_of.difference(new_inside_of)
        if entity_pre_leave.has_receivers_for(self):
            for leaving in leaves:
                for func, ret in entity_pre_leave.send(self, leaves=leaving):
                    if not ret:
                        return False
        self.position = pos
        self.is_inside_of = new_inside_of
        if entity_post_leave.has_receivers_for(self):
            for place in leaves:
                entity_post_leave.send(self, leaves=place)
        if entity_post_leave.has_receivers_for(self):
            for place in enters:
                entity_post_enter.send(self, enters=place)
        entity_post_move.send(self)
    
    def step_forward(self):
        pos, new_dir = self.position.destination2(self.STEP_LENGTH, self.direction)
        self.move_to(pos)
        self.direction = new_dir
    def step_backward(self):
        self.move_to(self.position.destination(-self.STEP_LENGTH, self.direction))
    def rotate(self, amount):
        self.direction = (self.direction + amount) % 360
        entity_rotated.send(self)