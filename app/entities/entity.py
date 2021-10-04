from pydantic import BaseModel, Field
from ordered_set import OrderedSet
from typing import ClassVar, Optional, Set
import osm_db
from . import entity_pre_move, entity_post_move, entity_pre_enter, entity_post_enter, entity_pre_leave, entity_post_leave, entity_rotated, entity_move_rejected, MoveValidationResult
from ..measuring import measure
from ..map import Map
from ..geometry_utils import to_shapely_point, to_latlon, closest_point_to, distance_between, bearing_to
from ..humanization_utils import describe_entity, format_number, format_rel_bearing
from ..services import config
from pygeodesy.ellipsoidalVincenty import LatLon

class Entity(BaseModel):
    use_step_sounds: ClassVar[bool] = False
    map: Map
    position: LatLon
    is_inside_of: "OrderedSet[Entity]" = Field(default_factory=OrderedSet)
    was_inside_of: "OrderedSet[Entity]" = Field(default_factory=OrderedSet)
    direction: float = 0.0

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self):
        return id(self)

    def move_to(self, pos, force=False):
        if not force and entity_pre_move.has_receivers_for(self):
            for func, ret in entity_pre_move.send(self, new_pos=pos):
                if ret is MoveValidationResult.reject:
                    entity_move_rejected.send(self)
                    return False
                elif ret is MoveValidationResult.cancel:
                    return False
        with measure("Inside of query"):
            new_inside_of = OrderedSet(entity for entity in self.map.intersections_at_position(pos, self.current_effective_width))
        if entity_pre_enter.has_receivers_for(self) or entity_post_enter.has_receivers_for(self):
            enters = new_inside_of.difference(self.is_inside_of)
        if enters and not force and entity_pre_enter.has_receivers_for(self):
            for func, ret in entity_pre_enter.send(self, enters=enters):
                if ret is MoveValidationResult.reject:
                    entity_move_rejected.send(self)
                    return False
                elif ret is MoveValidationResult.cancel:
                    return False
        if entity_pre_leave.has_receivers_for(self) or entity_post_leave.has_receivers_for(self):
            leaves = self.is_inside_of.difference(new_inside_of)
        if not force and entity_pre_leave.has_receivers_for(self) and leaves:
            for func, ret in entity_pre_leave.send(self, leaves=leaves):
                if ret is MoveValidationResult.reject:
                    entity_move_rejected.send(self)
                    return False
                elif ret is MoveValidationResult.cancel:
                    return False
        self.position = pos
        self.was_inside_of = OrderedSet(self.is_inside_of)
        # Note that we unfortunately can not assign the new_inside_of set directly as it has no defined ordering from the database, or rather, it has likely the wrong one.
        for leaving in leaves:
            self.is_inside_of.remove(leaving)
        for entering in enters:
            self.is_inside_of.add(entering)
        if leaves and entity_post_leave.has_receivers_for(self):
            entity_post_leave.send(self, leaves=leaves, enters=enters)
        if enters and entity_post_enter.has_receivers_for(self):
            entity_post_enter.send(self, enters=enters)
        entity_post_move.send(self)
    
    def move_by(self, pos_delta, force=False, direction=None):
        if not direction:
            direction = self.direction
        pos, new_dir = self.position.destination2(pos_delta, direction)
        if self.move_to(pos, force):
            self.set_direction(new_dir)
    
    def rotate(self, amount):
        self.set_direction(self.direction + amount)
    
    def set_direction(self, direction):
        self.direction = direction % 360
        entity_rotated.send(self)
    
    @property
    def cartesian_position(self):
        return self.map.project_latlon(self.position)
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

    def move_to_center_of(self, road):
        closest = self.closest_point_to(road.geometry)
        # Don't play the step sound for this movement command
        orig = self.__class__.use_step_sounds
        self.__class__.use_step_sounds = False
        self.move_to(closest, force=True)
        self.__class__.use_step_sounds = orig

    @property
    def current_effective_width(self):
        for candidate in reversed(self.is_inside_of):
            if candidate.is_road_like:
                return candidate.effective_width
        return None

    def spatial_relationship_to(self, entity, include_human=True):
        rel_bearing_human = None
        cur_distance_human = None
        entity_human = None
        closest_latlon = self.closest_point_to(entity.geometry)
        cur_distance = distance_between(closest_latlon, self.position)
        bearing = bearing_to(self.position, closest_latlon)
        rel_bearing = (bearing - self.direction) % 360
        if include_human:
            rel_bearing_human = format_rel_bearing(rel_bearing)
            cur_distance_human = format_number(cur_distance, config().presentation.distance_decimal_places)
            entity_human = describe_entity(entity)
        return SpatialRelationship(entity=entity, entity_human=entity_human, distance=cur_distance, distance_human=cur_distance_human, relative_bearing=rel_bearing, relative_bearing_human=rel_bearing_human, closest_point=closest_latlon)
        
Entity.update_forward_refs()

class SpatialRelationship(BaseModel):
    """Represents the distance and bearing, optionally with human readable representations of these values, to an entity."""
    distance: float
    relative_bearing: float
    entity: osm_db.Entity
    closest_point: LatLon
    distance_human: Optional[str] = None
    relative_bearing_human: Optional[str] = None
    entity_human: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
    
