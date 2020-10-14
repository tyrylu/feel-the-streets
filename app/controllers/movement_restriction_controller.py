from ..entities import entity_pre_leave, entity_pre_enter
from ..services import config
from osm_db import Enum

class MovementRestrictionController:

    def __init__(self, restricted):
        self._restricted_entity = restricted
        entity_pre_leave.connect(self._entity_pre_leave)
        entity_pre_enter.connect(self._entity_pre_enter)

    def _entity_pre_enter(self, sender, enters):
        if not config().navigation.disallow_entering_sidewalks:
            return True
        for place in enters:
            if place.discriminator == "Road" and place.value_of_field("type") == Enum.with_name("RoadType").value_for_name("footway"):
                return False
        return True

    def _entity_pre_leave(self, sender, leaves):
        if not config().navigation.disallow_leaving_roads or sender is not self._restricted_entity:
            return True
        to_be_left_roads = [e for e in leaves if e.is_road_like]
        if not to_be_left_roads:
            return True # We're only interested in leaving roads
        remaining_road_like = [thing for thing in sender.inside_of_roads if thing not in to_be_left_roads]
        # Are we leaving a road like thing and no other road like thing remains?
        return len(remaining_road_like) > 0
        