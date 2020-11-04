from .interesting_entities_controller import request_interesting_entities
from ..entities import entity_pre_enter, MoveValidationResult
from ..geometry_utils import get_crossing_point, to_latlon
from ..entity_utils import filter_important_roads

class PositionAdjustmentController:
    def __init__(self, controlled):
        self._controlled = controlled
        entity_pre_enter.connect(self._entity_pre_enter)
    
    def _entity_pre_enter(self, sender, enters):
        for place in enters:
            if place.is_road_like:
                current_roads = filter_important_roads(self._controlled.inside_of_roads)
                if not current_roads:
                    continue
                crossing_possibilities = [r for r in request_interesting_entities.send(self)[0][1] if r.is_road_like and r not in enters and r not in self._controlled.is_inside_of]
                intersection = get_crossing_point(current_roads[-1], place, crossing_possibilities)
                if intersection:
                    self._controlled.move_to(to_latlon(intersection), force=True)
                    return MoveValidationResult.cancel
        return MoveValidationResult.accept
        