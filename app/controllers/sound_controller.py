import collections, math
import logging
import random
from typing import DefaultDict, Dict
import anglr
from blinker import Signal
import shapely.wkb as wkb
from osm_db import Enum
from ..services import sound, config, menu_service, map
from ..geometry_utils import to_latlon
from ..entities import entity_post_move, entity_post_enter, entity_post_leave, entity_rotated, entity_move_rejected, Entity
from ..humanization_utils import describe_entity
from .interesting_entities_controller import interesting_entity_out_of_range, interesting_entity_in_range, request_interesting_entities

DEFAULT_STEPS_GROUP = "steps_unknown"

leave_disallowed_sound_played = Signal()
interesting_entity_sound_not_found = Signal()

def get_sound(entity):
    if entity.discriminator == "Shop":
        return "shop"
    elif entity.discriminator == "Land":
        return "land"
    elif entity.discriminator == "Amenity" and entity.value_of_field("type") == Enum.with_name("AmenityType").value_for_name("waste_basket"):
        return "trashcan"
    else:
        return None

log = logging.getLogger(__name__)

class SoundController:
    
    def __init__(self, person):
        self._point_of_view: Entity = person
        self._load_sound_played = False
        self._groups_map: DefaultDict[Entity, Dict[Entity, str]] = collections.defaultdict(dict)
        self._interesting_sounds = collections.defaultdict(dict) # A mapping which maps a sound originating entity, some entity which was a reason for the sound source generation (e. g. the second part of a crossing tuple) to the sound source.
        self._interesting_roads = set()
        entity_post_move.connect(self.post_move)
        entity_post_enter.connect(self.post_enter)
        entity_post_leave.connect(self.post_leave)
        entity_rotated.connect(self._rotated)
        entity_move_rejected.connect(self._entity_move_rejected)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
        interesting_entity_out_of_range.connect(self._interesting_entity_out_of_range)
        menu_service().menu_item_with_name("toggle_play_sounds_for_interesting_objects").triggered.connect(self._play_sounds_triggered)
        menu_service().menu_item_with_name("toggle_play_crossing_sounds").triggered.connect(self._play_crossing_sounds_triggered)

    def post_move(self, sender):
        if not self._load_sound_played:
            sound().play("loaded")
            self._load_sound_played = True
        x, y = sender.cartesian_position
        if self._point_of_view is sender:
            sound().listener.set_position([x, y, 0])
            for entity, source in self._interesting_sounds.items():
                if entity.is_road_like: continue # We're not moving the road crossing sounds with the listener
                x, y = map().project_latlon(self._point_of_view.closest_point_to(entity.geometry))
                # For classic interesting object sounds, we'll always get only one sound sou        rce without a specifying entity.
                source = source[None]
                source.set_position([x, y, 0])
        if not sender.use_step_sounds:
            return
        group_stack = self._groups_map[sender]
        if len(group_stack):
            group = DEFAULT_STEPS_GROUP
            # Use the latest non-default steps group
            for group_candidate in reversed(group_stack.values()):
                if group_candidate != DEFAULT_STEPS_GROUP:
                    group = group_candidate
                    break
        else:
            group = None
        if group:
            sound().play_random_from_group(group, x=x, y=y, z=0)

    def post_enter(self, sender, enters):
        if not sender.use_step_sounds:
            return
        for place in enters:
            self._handle_enter_into(sender, place)
        
    def _handle_enter_into(self, sender, enters):
        base_group = None
        if enters.is_road_like:
            # Simulate that all the currently interesting roads just became interesting.
            for road in self._interesting_roads:
                self._maybe_spawn_crossing_sound_for_road(enters, road)
            if enters.value_of_field("type") == Enum.with_name("RoadType").value_for_name("path"):
                base_group = "steps_path"
            else:
                base_group = "steps_road"
        if base_group:
            count = sound().get_group_size(base_group)
            group = "%s.%02d"%(base_group, random.randint(1, count))
        else:
            group = DEFAULT_STEPS_GROUP
        self._groups_map[sender][enters] = group
    
    def post_leave(self, sender, leaves, enters):
        if not sender.use_step_sounds:
            return
        for place in leaves:
            self._handle_leave_of(sender, place)
        
    def _handle_leave_of(self, sender, leaves):
        if leaves.is_road_like:
            if sender in self._groups_map:
                if leaves not in self._groups_map[sender]:
                    log.warn("Entity %s about to be deleted from the sounds stack, but it was not in it in the first place.", describe_entity(leaves))
                    return
                del self._groups_map[sender][leaves]
            if leaves in self._interesting_sounds:
                for source in self._interesting_sounds[leaves].values():
                    source.stop()
                del self._interesting_sounds[leaves]

    def _rotated(self, sender):
        if self._point_of_view is sender:
            rounded_direction = int(sender.direction)
            anti_clockwise_angle = (360 - rounded_direction) +90
            angle = anglr.Angle(anti_clockwise_angle, "degrees")
            sound().listener.set_orientation([angle.x, 0, -angle.y, 0, 1, 0]) # The mapping to the mathematical cartesian coordinate system is x,z,-y

    def _entity_move_rejected(self, sender):
        x, y = sender.cartesian_position
        sound().play("leave_disallowed", x=x, y=y, z=0)
        leave_disallowed_sound_played.send(self, because_of=sender)

    def _interesting_entity_in_range(self, sender, entity):
        if not entity.is_road_like and config().presentation.play_sounds_for_interesting_objects:
            self._spawn_sound_for(entity)   
        elif entity.is_road_like:
            self._interesting_roads.add(entity)
            if config().presentation.play_crossing_sounds:
                self._spawn_crossing_sound_for(entity)

    
    def _spawn_crossing_sound_for(self, road):
        roads = [e for e in self._point_of_view.inside_of_roads if e != road]
        for current_road in roads:
            self._maybe_spawn_crossing_sound_for_road(current_road, road)
    
    def _maybe_spawn_crossing_sound_for_road(self, current_road, interesting_road):
        if describe_entity(current_road) == describe_entity(interesting_road):
            return # We entered a part of a split road which intersects with the old one, but we're pretending that those part differences don't exist, so don't play a sound for it.
        sounds = self._interesting_sounds.get(interesting_road, {})
        if current_road in sounds:
            return # We will not spawn a sound for a crossing of roads b and a if we already have one for a and b
        current_sounds = self._interesting_sounds.get(current_road, {})
        if interesting_road in current_sounds:
            return # We already spawned this one
        current_road_geom = wkb.loads(current_road.geometry)
        interesting_road_geom = wkb.loads(interesting_road.geometry)
        intersection = current_road_geom.intersection(interesting_road_geom)
        if not intersection:
            return # There's no intersection of the roads
        dest_latlon = None
        if intersection.geom_type == "Point":
            dest_latlon = to_latlon(intersection)
        else:
            log.warning("No way how to determine the point to spawn the sound at for intersection %s.", intersection)
        if dest_latlon:
            x, y = map().project_latlon(dest_latlon)
            snd = sound().play("road_turn", x=x, y=y, z=0, set_loop=True)
            self._interesting_sounds[current_road][interesting_road] = snd


    def _spawn_sound_for(self, entity):
        sound_name = get_sound(entity)
        if not sound_name:
            log.warning("Could not determine sound for %s", describe_entity(entity))
            interesting_entity_sound_not_found.send(self, entity=entity)
            return
        x, y = map().project_latlon(self._point_of_view.closest_point_to(entity.geometry))
        self._interesting_sounds[entity][None] = sound().play(sound_name, set_loop=True, x=x, y=y, z=0)

    def _interesting_entity_out_of_range(self, sender, entity):
        if config().presentation.play_crossing_sounds:
            if entity in self._interesting_roads:
                self._interesting_roads.remove(entity)
        if not config().presentation.play_sounds_for_interesting_objects and not config().presentation.play_crossing_sounds: return
        if entity in self._interesting_sounds:
            for source in self._interesting_sounds[entity].values():
                source.stop()
            del self._interesting_sounds[entity]

    def _play_sounds_triggered(self, checked):
        if not checked:
            self._stop_interesting_sounds(False)
        else:
            self._spawn_interesting_sounds()

    def _stop_interesting_sounds(self, stop_road_likes):
        to_remove = []
        for entity, sounds in self._interesting_sounds.items():
            if entity.is_road_like != stop_road_likes: continue
            for sound in sounds.values():
                sound.stop()
            to_remove.append(entity)
        for entity in to_remove:
            del self._interesting_sounds[entity]


    def _spawn_interesting_sounds(self):
        for entity in request_interesting_entities.send(self)[0][1]:
            if not entity.is_road_like:
                self._spawn_sound_for(entity)

    def _play_crossing_sounds_triggered(self, checked):
        if not checked:
            self._stop_interesting_sounds(True)
        else:
            self._spawn_crossing_sounds()

    def _spawn_crossing_sounds(self):
        for entity in request_interesting_entities.send(self)[0][1]:
            if entity.is_road_like:
                self._spawn_crossing_sound_for(entity)