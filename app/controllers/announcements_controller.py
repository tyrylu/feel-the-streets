import shapely.wkb as wkb
from ..services import speech, config
from ..entities import entity_post_enter, entity_post_leave, entity_rotated
from ..controllers.interesting_entities_controller import interesting_entity_in_range
from ..humanization_utils import describe_entity, format_number, describe_relative_angle, TemplateType, describe_angle_as_turn_instructions
from ..geometry_utils import bearing_to, get_line_segments, merge_similar_line_segments, find_closest_line_segment_of, calculate_absolute_distances

def is_road_like(entity):
    return entity.discriminator in {"Road", "ServiceRoad"}

class AnnouncementsController:
    def __init__(self, pov):
        self._point_of_view = pov
        entity_post_enter.connect(self._on_post_enter)
        entity_post_leave.connect(self._on_post_leave)
        entity_rotated.connect(self._on_rotated)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
    
    def _on_post_enter(self, sender, enters):
        if sender is self._point_of_view:
            speech().speak(_("You are entering {enters}.").format(enters=describe_entity(enters)))
            if is_road_like(enters):
                print("Is road like.")
                self._announce_possible_turn_opportunity(enters)
            
    def _announce_possible_turn_opportunity(self, new_road):
        current_roads = [r for r in self._point_of_view.is_inside_of if r.discriminator in {"Road", "ServiceRoad"} and r != new_road]
        if not current_roads: return
        current_road = current_roads[0] # Use the first, hopefully the one which the user was walking the longest time.
        new_segments = merge_similar_line_segments(get_line_segments(wkb.loads(new_road.geometry)), config().presentation.angle_decimal_places)
        current_segments = merge_similar_line_segments(get_line_segments(wkb.loads(current_road.geometry)), config().presentation.angle_decimal_places)
        closest_new_segment = find_closest_line_segment_of(new_segments, self._point_of_view.position_point)
        closest_new_segment.calculate_angle()
        new_angle = abs(closest_new_segment.angle - self._point_of_view.direction)
        from_start, to_end = calculate_absolute_distances(new_segments, self._point_of_view)
        meaningful_directions = []
        if from_start > 10:
            meaningful_directions.append((describe_angle_as_turn_instructions((new_angle + 180)%360, config().presentation.angle_decimal_places), format_number(from_start, config().presentation.distance_decimal_places)))
        if to_end > 10:
            meaningful_directions.append((describe_angle_as_turn_instructions(new_angle, config().presentation.angle_decimal_places), format_number(to_end, config().presentation.distance_decimal_places)))
        if len(meaningful_directions) == 1:
            ((dir, dist),) = meaningful_directions
            speech().speak(_("You could turn {direction} and continue for {distance} meters.").format(direction=dir, distance=dist))
        elif len(meaningful_directions) == 2:
            ((dir1, dist1), (dir2, dist2)) = meaningful_directions
            speech().speak(_("You could turn {direction1} and continue for {distance1} meters, or you could turn {direction2} and continue for {distance2} meters.").format(direction1=dir1, distance1=dist1, direction2=dir2, distance2=dist2))






    def _on_post_leave(self, sender, leaves):
        if sender is self._point_of_view:
            speech().speak(_("You are leaving {leaves}").format(leaves=describe_entity(leaves)))

    def _on_rotated(self, sender):
        if self._point_of_view is sender:
            speech().speak(_("{degrees} degrees").format(degrees=format_number(sender.direction, config().presentation.angle_decimal_places)))

    def _interesting_entity_in_range(self, sender, entity):
        if not config().presentation.announce_interesting_objects: return
        closest_point = self._point_of_view.closest_point_to(entity.geometry)
        bearing = bearing_to(self._point_of_view.position, closest_point)
        rel_bearing = (bearing - self._point_of_view.direction) % 360
        speech().speak(_("{angle_description} is a {entity_description}").format(angle_description=describe_relative_angle(rel_bearing), entity_description=describe_entity(entity, template_type=TemplateType.short)))
