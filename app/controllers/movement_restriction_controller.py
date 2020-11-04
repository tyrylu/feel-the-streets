from ..entities import entity_pre_leave, entity_pre_enter, MoveValidationResult
from ..services import config
from ..entity_utils import filter_important_roads, is_footway, get_last_important_road
from ..geometry_utils import get_meaningful_turns, get_smaller_turn

class MovementRestrictionController:

    def __init__(self, restricted):
        self._restricted_entity = restricted
        entity_pre_leave.connect(self._entity_pre_leave)
        entity_pre_enter.connect(self._entity_pre_enter)

    def _entity_pre_enter(self, sender, enters):
        if sender is not self._restricted_entity or not config().navigation.try_avoid_sidewalks:
            return MoveValidationResult.accept # You can enter whatever you wish.
        for place in enters:
            if place.is_road_like and is_footway(place) and not self._should_allow_entrance_to_footway(place):
                return MoveValidationResult.reject
        return MoveValidationResult.accept

    def _should_allow_entrance_to_footway(self, footway):
        if not self._restricted_entity.inside_of_roads:
            return True # In this case, we'll be at least on some road
        important_rroad = get_last_important_road(self._restricted_entity.inside_of_roads)
        footway_turn = get_smaller_turn(get_meaningful_turns(footway, self._restricted_entity, zero_turn_is_meaningful=True, ignore_length=True))
        road_turn = get_smaller_turn(get_meaningful_turns(important_rroad, self._restricted_entity, zero_turn_is_meaningful=True, ignore_length=True))
        angle_diff = abs(footway_turn[2] - road_turn[2])
        # Entering sidewalks which lead to somewhere else is allowed - we might want to cross them
        return 5 < angle_diff < 355


    def _entity_pre_leave(self, sender, leaves):
        if not config().navigation.disallow_leaving_roads or sender is not self._restricted_entity:
            return MoveValidationResult.accept
        to_be_left_roads = [e for e in leaves if e.is_road_like]
        if not to_be_left_roads:
            return MovementRestrictionController.accept # We're only interested in leaving roads
        remaining_road_like = [thing for thing in filter_important_roads(sender.inside_of_roads) if thing not in to_be_left_roads]
        # Are we leaving a road like thing and no other road like thing remains?
        return MoveValidationResult.accept if len(remaining_road_like) > 0 else MoveValidationResult.reject
        