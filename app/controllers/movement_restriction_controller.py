from ..entities import entity_pre_leave
from ..services import config

class MovementRestrictionController:

    def __init__(self, restricted):
        self._restricted_entity = restricted
        entity_pre_leave.connect(self._entity_pre_leave)

    def _entity_pre_leave(self, sender, leaves):
        if not config().navigation.disallow_leaving_roads or sender is not self._restricted_entity:
            return True
        remaining_road_like = [thing for thing in sender.inside_of_roads if thing is not leaves]
        # Are we leaving a road like thing and no other road like thing remains?
        if leaves.is_road_like and not remaining_road_like:
            return False
        else:
            return True
        