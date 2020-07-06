from ..entities import entity_pre_leave
from ..services import config

class MovementRestrictionController:

    def __init__(self, restricted):
        self._restricted_entity = restricted
        entity_pre_leave.connect(self._entity_pre_leave)

    def _entity_pre_leave(self, sender, leaves):
        road_like_discriminators = {"Road", "ServiceRoad", "Track"}
        if not config().disallow_leaving_roads or sender is not self._restricted_entity:
            return True
        remaining_road_like = [thing for thing in sender.is_inside_of if thing is not leaves and thing.discriminator in road_like_discriminators]
        # Are we leaving a road like thing and no other road like thing remains?
        if leaves.discriminator in road_like_discriminators and not remaining_road_like:
            return False
        else:
            return True
        