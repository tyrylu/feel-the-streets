import enum
import collections
import shapely.wkb as wkb
from ..services import speech, config
from ..entities import entity_post_enter, entity_post_leave, entity_rotated
from ..humanization_utils import describe_entity, format_number, describe_relative_angle, TemplateType, describe_angle_as_turn_instructions
from ..geometry_utils import bearing_to, get_meaningful_turns, get_smaller_turn
from ..entity_utils import get_last_important_road, filter_important_roads
from .interesting_entities_controller import interesting_entity_in_range
from .sound_controller import interesting_entity_sound_not_found

LARGE_TURN_THRESHOLD = 10

class EntranceKind(enum.Enum):
    initial = 0
    continuation = 1
    turn = 2

class LeaveKind(enum.Enum):
    last = 0
    continuation = 1
    turn = 2

class AnnouncementsController:
    def __init__(self, pov):
        self._point_of_view = pov
        self._description_counts = collections.Counter()
        self._do_not_announce_leave_of = set()
        self._announced_turns = False
        entity_post_enter.connect(self._on_post_enter)
        entity_post_leave.connect(self._on_post_leave)
        entity_rotated.connect(self._on_rotated)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
        interesting_entity_sound_not_found.connect(self._interesting_entity_sound_not_found)
    
    def _on_post_enter(self, sender, enters):
        if sender is not self._point_of_view:
            return
        entered_road = False
        description_groups = collections.defaultdict(list)
        for place in enters:
            description_groups[describe_entity(place)].append(place)
        for desc, places in description_groups.items():
            self._description_counts[desc] += len(places)
            if self._description_counts[desc] > 1 and (not places[0].is_road_like or self._classify_enter_into(places[0], enters)[0] is not EntranceKind.turn): # The place should not be announced if it was announced before and it is not a road which has significantly different direction than the current one
                continue
            if places[0].is_road_like:
                self._announced_turns = False
                classification, maybe_road = self._select_most_important_classification(places, enters)
                if classification == EntranceKind.initial:
                    speech().speak(_("You are entering {enters}.").format(enters=desc))
                elif classification == EntranceKind.continuation:
                    self._do_not_announce_leave_of.add(maybe_road)
                    speech().speak(_("{before} continues as {after}.").format(before=describe_entity(maybe_road), after=desc))
                elif classification == EntranceKind.turn:
                    speech().speak(_("You are crossing {enters}.").format(enters=desc))
                entered_road = True
                self._announce_possible_turn_opportunity(places)
            else:
                speech().speak(_("You are entering {enters}.").format(enters=desc))
        if entered_road:
            self._announce_possible_continuation_opportunity(enters)
    
    def _select_most_important_classification(self, places, enters):
        classifications = [self._classify_enter_into(p, enters) for p in places]
        # If we have a turn, we want to know about that
        if any([cl[0] is EntranceKind.turn for cl in classifications]):
            return (EntranceKind.turn, None)
        # Now, we either have all continuations or inital entrances
        return classifications[0]


    def _classify_enter_into(self, place, enters):
        turns = get_meaningful_turns(place, self._point_of_view, zero_turn_is_meaningful=True, ignore_length=True)
        road_diff = get_smaller_turn(turns)[2]
        if 0 <= abs(road_diff) <= LARGE_TURN_THRESHOLD:
            important_roads = filter_important_roads(self._point_of_view.inside_of_roads)
            old_roads = [r for r in important_roads if r not in enters]
            if not old_roads:
                return EntranceKind.initial, None
            else:
                return EntranceKind.continuation, old_roads[-1]
        else:
            return EntranceKind.turn, None
                        
    def _classify_leave_of(self, place):
        if not self._point_of_view.inside_of_roads:
            return LeaveKind.last, None
        last_important = get_last_important_road(self._point_of_view.inside_of_roads)
        turns = get_meaningful_turns(place, self._point_of_view, zero_turn_is_meaningful=True, ignore_length=True)
        road_diff = get_smaller_turn(turns)[2]
        if 0 <= abs(road_diff) <= LARGE_TURN_THRESHOLD:
            return LeaveKind.continuation, last_important
        else:
            return LeaveKind.turn, None

    def _announce_possible_continuation_opportunity(self, newly_entered):
        roads_before_entering = [r for r in self._point_of_view.inside_of_roads if r not in newly_entered]
        if len(roads_before_entering) < 1:
            return # Before entering the current roads, the person was not on a road at all, so it's definitely not an event of a continuation possibility.
        current_road = get_last_important_road(roads_before_entering)
        turns = get_meaningful_turns(current_road, self._point_of_view, zero_turn_is_meaningful=True)
        if not turns:
            speech().speak(_("{0} ends here.").format(describe_entity(current_road)))
            return
        current_dir_info = min(turns, key=lambda i: abs(i[2]))
        if abs(current_dir_info[2]) < 90:
            if self._announced_turns:
                speech().speak(_("Or, you can continue along the current road for another {} meters.").format(current_dir_info[1]))
            else:
                speech().speak(_("You can continue along the current road for another {} meters.").format(current_dir_info[1]))
        else:
            speech().speak(_("{0} ends here.").format(describe_entity(current_road)))



    def _announce_possible_turn_opportunity(self, new_roads):
        meaningful_directions = []
        for new_road in new_roads:
            meaningful_directions.extend(get_meaningful_turns(new_road, self._point_of_view))
        if meaningful_directions:
            self._announced_turns = True
        if len(meaningful_directions) == 1:
            ((dir, dist, _angle_diff, _road),) = meaningful_directions
            speech().speak(_("You could turn {direction} and continue for {distance} meters.").format(direction=dir, distance=dist))
        elif len(meaningful_directions) == 2:
            ((dir1, dist1, _angle_diff1, _road1), (dir2, dist2, _angle_diff2, _road2)) = meaningful_directions
            speech().speak(_("You could turn {direction1} and continue for {distance1} meters, or you could turn {direction2} and continue for {distance2} meters.").format(direction1=dir1, distance1=dist1, direction2=dir2, distance2=dist2))






    def _on_post_leave(self, sender, leaves, enters):
        if sender is not self._point_of_view:
            return
        announced_leave = False
        for place in leaves:
            desc = describe_entity(place)
            self._description_counts[desc] -= 1
            if self._description_counts[desc] == 0:
                del self._description_counts[desc]
            if self._description_counts[desc] > 0 and (not place.is_road_like or self._classify_leave_of(place)[0] is not LeaveKind.turn):
                continue # Say the message only if we aren't in an entity with the same description because of a different entity and it is not a significantly different road
            if place in self._do_not_announce_leave_of:
                self._do_not_announce_leave_of.remove(place)
            else:
                announced_leave = True
                if place.is_road_like:
                    classification, maybe_road = self._classify_leave_of(place)
                    if classification == LeaveKind.turn:
                        speech().speak(_("You crossed {leaves}.").format(leaves=desc))
                    elif classification == LeaveKind.continuation:
                        speech().speak(_("{before} continues as {after}.").format(before=desc, after=describe_entity(maybe_road)))
                    elif classification == LeaveKind.last:
                        speech().speak(_("You are leaving {leaves}").format(leaves=describe_entity(place)))
                else:
                    speech().speak(_("You are leaving {leaves}").format(leaves=describe_entity(place)))
        if announced_leave and config().presentation.announce_current_object_after_leaving_other:
            if not self._point_of_view.is_inside_of:
                speech().speak(_("Now, your location is not known."))
            else:
                now_before_enters = [e for e in self._point_of_view.is_inside_of if e not in enters]
                if now_before_enters:
                    is_on = now_before_enters[-1]
                else:
                    is_on = self._point_of_view.is_inside_of[-1]
                speech().speak(_("Now, you're on {}.").format(describe_entity(is_on)))

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