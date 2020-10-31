import collections
import shapely.wkb as wkb
from ..services import speech, config
from ..entities import entity_post_enter, entity_post_leave, entity_rotated
from ..humanization_utils import describe_entity, format_number, describe_relative_angle, TemplateType, describe_angle_as_turn_instructions
from ..geometry_utils import bearing_to, get_meaningful_turns
from ..entity_utils import get_last_important_road
from .interesting_entities_controller import interesting_entity_in_range
from .sound_controller import interesting_entity_sound_not_found

class AnnouncementsController:
    def __init__(self, pov):
        self._point_of_view = pov
        self._description_counts = collections.Counter()
        entity_post_enter.connect(self._on_post_enter)
        entity_post_leave.connect(self._on_post_leave)
        entity_rotated.connect(self._on_rotated)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
        interesting_entity_sound_not_found.connect(self._interesting_entity_sound_not_found)
    
    def _on_post_enter(self, sender, enters):
        if sender is self._point_of_view:
            entered_road = False
            for place in enters:
                desc = describe_entity(place)
                self._description_counts[desc] += 1
                if self._description_counts[desc] > 1: # After adding the current entry we find out that we already said it
                    continue
                speech().speak(_("You are entering {enters}.").format(enters=desc))
                if place.is_road_like:
                    entered_road = True
                    self._announce_possible_turn_opportunity(place)
            if entered_road:
                self._announce_possible_continuation_opportunity(enters)
            
    def _announce_possible_continuation_opportunity(self, newly_entered):
        roads_before_entering = [r for r in self._point_of_view.inside_of_roads if r not in newly_entered]
        if len(roads_before_entering) < 1:
            return # Before entering the current roads, the person was not on a road at all, so it's definitely not an event of a continuation possibility.
        current_road = get_last_important_road(roads_before_entering)
        turns = get_meaningful_turns(current_road, self._point_of_view, zero_turn_is_meaningful=True)
        if not turns:
            return
        current_dir_info = min(turns, key=lambda i: abs(i[2]))
        if abs(current_dir_info[2]) < 90:
            speech().speak(_("Or, you can continue along the current road for another {} meters.").format(current_dir_info[1]))



    def _announce_possible_turn_opportunity(self, new_road):
        meaningful_directions = get_meaningful_turns(new_road, self._point_of_view)
        if len(meaningful_directions) == 1:
            ((dir, dist, _angle_diff, _road),) = meaningful_directions
            speech().speak(_("You could turn {direction} and continue for {distance} meters.").format(direction=dir, distance=dist))
        elif len(meaningful_directions) == 2:
            ((dir1, dist1, _angle_diff1, _road1), (dir2, dist2, _angle_diff2, _road2)) = meaningful_directions
            speech().speak(_("You could turn {direction1} and continue for {distance1} meters, or you could turn {direction2} and continue for {distance2} meters.").format(direction1=dir1, distance1=dist1, direction2=dir2, distance2=dist2))






    def _on_post_leave(self, sender, leaves):
        if sender is self._point_of_view:
            announced_leave = False
            for place in leaves:
                desc = describe_entity(place)
                self._description_counts[desc] -= 1
                if self._description_counts[desc] == 0:
                    del self._description_counts[desc]
                if self._description_counts[desc] > 0:
                    continue # Say the message only if we aren't in an entity with the same description because of a different entity
                announced_leave = True
                speech().speak(_("You are leaving {leaves}").format(leaves=describe_entity(place)))
            if announced_leave and config().presentation.announce_current_object_after_leaving_other:
                if not self._point_of_view.is_inside_of:
                    speech().speak(_("Now, your location is not known."))
                else:
                    speech().speak(_("Now, you're on {}.").format(describe_entity(self._point_of_view.is_inside_of[-1])))

    def _on_rotated(self, sender):
        if self._point_of_view is sender:
            speech().speak(_("{degrees} degrees").format(degrees=format_number(sender.direction, config().presentation.angle_decimal_places)), add_to_history=False)

    def _interesting_entity_in_range(self, sender, entity):
        if not config().presentation.announce_interesting_objects: return
        self._announce_interesting_entity(entity)

    def _announce_interesting_entity(self, entity):
        if entity.is_road_like: return
        closest_point = self._point_of_view.closest_point_to(entity.geometry)
        bearing = bearing_to(self._point_of_view.position, closest_point)
        rel_bearing = (bearing - self._point_of_view.direction) % 360
        speech().speak(_("{angle_description} is a {entity_description}").format(angle_description=describe_relative_angle(rel_bearing), entity_description=describe_entity(entity, template_type=TemplateType.short)))

    def _interesting_entity_sound_not_found(self, sender, entity):
        if not config().presentation.announce_interesting_objects:
            self._announce_interesting_entity(entity)