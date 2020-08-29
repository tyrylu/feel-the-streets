import collections
import logging
import random
from typing import DefaultDict, Dict
import anglr
from osm_db import Enum
from ..services import sound, config, menu_service
from ..entities import entity_post_move, entity_post_enter, entity_post_leave, entity_rotated, entity_move_rejected, Entity
from ..humanization_utils import describe_entity
from .interesting_entities_controller import interesting_entity_out_of_range, interesting_entity_in_range, request_interesting_entities

def get_sound(entity):
    if entity.discriminator == "Shop":
        return "shop"
    else:
        return None

log = logging.getLogger(__name__)

class SoundController:
    
    def __init__(self, person):
        self._point_of_view: Entity = person
        self._load_sound_played = False
        self._groups_map: DefaultDict[Entity, Dict[Entity, str]] = collections.defaultdict(dict)
        self._interesting_sounds = {}
        entity_post_move.connect(self.post_move)
        entity_post_enter.connect(self.post_enter)
        entity_post_leave.connect(self.post_leave)
        entity_rotated.connect(self._rotated)
        entity_move_rejected.connect(self._entity_move_rejected)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
        interesting_entity_out_of_range.connect(self._interesting_entity_out_of_range)
        menu_service().menu_item_with_name("toggle_play_sounds_for_interesting_objects").triggered.connect(self._play_sounds_triggered)

    def post_move(self, sender):
        if not self._load_sound_played:
            sound().play("loaded")
            self._load_sound_played = True
        cartesian = sender.position.toCartesian()
        x, y, z = (cartesian.x, cartesian.y, cartesian.z)
        if self._point_of_view is sender:
            sound().listener.set_position([x, y, z])
            for entity, source in self._interesting_sounds.items():
                cartesian = self._point_of_view.closest_point_to(entity.geometry).toCartesian()
                source.set_position([cartesian.x, cartesian.y, cartesian.z])
        if not sender.use_step_sounds:
            return
        group_stack = self._groups_map[sender]
        if len(group_stack):
            group = group_stack[list(group_stack.keys())[-1]]
        else:
            group = None
        if group:
            sound().play_random_from_group(group, x=x, y=y, z=z)

    def post_enter(self, sender, enters):
        if not sender.use_step_sounds:
            return
        base_group = None
        if enters.discriminator == "Road":
            if enters.value_of_field("type") == Enum.with_name("RoadType").value_for_name("path"):
                base_group = "steps_path"
            else:
                base_group = "steps_road"
        if base_group:
            count = sound().get_group_size(base_group)
            group = "%s.%02d"%(base_group, random.randint(1, count))
        else:
            group = "steps_unknown"
        self._groups_map[sender][enters] = group
    
    def post_leave(self, sender, leaves):
        if not sender.use_step_sounds:
            return
        if leaves.discriminator == "Road":
            if sender not in self._groups_map:
                print("Already left %s."%sender)
            else:
                del self._groups_map[sender][leaves]

    def _rotated(self, sender):
        if self._point_of_view is sender:
            angle = anglr.Angle(sender.direction, "degrees")
            print(f"Setting listener forward vector to {angle.x} {angle.y}")
            sound().listener.set_orientation([-angle.y, 0, -angle.x, 0, 1, 0]) # The mapping to the mathematical cartesian coordinate system is x,z,y

    def _entity_move_rejected(self, sender):
        cartesian = sender.position.toCartesian()
        sound().play("leave_disallowed", x=cartesian.x, y=cartesian.y, z=cartesian.z)

    def _interesting_entity_in_range(self, sender, entity):
        if not config().presentation.play_sounds_for_interesting_objects: return
        self._spawn_sound_for(entity)
    
    def _spawn_sound_for(self, entity):
        sound_name = get_sound(entity)
        if not sound_name:
            log.warn("Could not determine sound for %s", describe_entity(entity))
            return
        cartesian = self._point_of_view.closest_point_to(entity.geometry).toCartesian()
        self._interesting_sounds[entity] = sound().play(sound_name, set_loop=True, x=cartesian.x, y=cartesian.y, z=cartesian.z)

    def _interesting_entity_out_of_range(self, sender, entity):
        if not config().presentation.play_sounds_for_interesting_objects: return
        if entity in self._interesting_sounds:
            self._interesting_sounds[entity].stop()
            del self._interesting_sounds[entity]

    def _play_sounds_triggered(self, checked):
        if not checked:
            self._stop_interesting_sounds()
        else:
            self._spawn_interesting_sounds()

    def _stop_interesting_sounds(self):
        for sound in self._interesting_sounds.values():
            sound.stop()
        self._interesting_sounds.clear()

    def _spawn_interesting_sounds(self):
        for entity in request_interesting_entities.send(self)[0][1]:
            self._spawn_sound_for(entity)