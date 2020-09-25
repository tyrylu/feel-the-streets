from pydantic import BaseModel, Field
from typing import ClassVar, Set
from . import entity_pre_move, entity_post_move, entity_pre_enter, entity_post_enter, entity_pre_leave, entity_post_leave, entity_rotated, entity_move_rejected
from ..measuring import measure
from ..map import Map
from ..geometry_utils import to_shapely_point, to_latlon, closest_point_to
from pygeodesy.ellipsoidalVincenty import LatLon


class Entity(BaseModel):
    use_step_sounds: ClassVar[bool] = False
    map: Map
    position: LatLon
    is_inside_of: "Set[Entity]" = Field(default_factory=set)
    direction: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self):
        return id(self)

    def move_to(self, pos, force=False):
        if not force and entity_pre_move.has_receivers_for(self):
            for func, ret in entity_pre_move.send(self, new_pos=pos):
                if not ret:
                    entity_move_rejected.send(self)
                    return False
        with measure("Inside of query"):
            new_inside_of = set(entity for entity in self.map.intersections_at_position(pos))
        if entity_pre_enter.has_receivers_for(self) or entity_post_enter.has_receivers_for(self):
            enters = new_inside_of.difference(self.is_inside_of)
        if not force and entity_pre_enter.has_receivers_for(self):
            for entered in enters:
                for func, ret in entity_pre_enter.send(self, enters=entered):
                    if not ret:
                        entity_move_rejected.send(self)
                        return False
        if entity_pre_leave.has_receivers_for(self) or entity_post_leave.has_receivers_for(self):
            leaves = self.is_inside_of.difference(new_inside_of)
        if not force and entity_pre_leave.has_receivers_for(self):
            for leaving in leaves:
                for func, ret in entity_pre_leave.send(self, leaves=leaving):
                    if not ret:
                        entity_move_rejected.send(self)
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
    
    def move_by(self, pos_delta, force=False):
        pos, new_dir = self.position.destination2(pos_delta, self.direction)
        if self.move_to(pos, force):
            self.direction = new_dir
    
    def rotate(self, amount):
        self.set_direction((self.direction + amount) % 360)
    
    def set_direction(self, direction):
        self.direction = direction
        entity_rotated.send(self)
    
    @property
    def cartesian_position(self):
        cartesian = self.position.toCartesian()
        return cartesian.x, cartesian.y, cartesian.z

    def closest_point_to(self, geometry, convert_geometry=True):
        return to_latlon(closest_point_to(self.position_point, geometry, convert_geometry))

    @property
    def position_point(self):
        """The entity's position as a shapely Point."""
        return to_shapely_point(self.position)

    @property
    def inside_of_roads(self):
        return [r for r in self.is_inside_of if r.is_road_like]

Entity.update_forward_refs()