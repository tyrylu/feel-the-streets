from ..entities import entity_post_move, entity_rotated
from ..services import map

class LastLocationController:

    def __init__(self, pov):
        self._point_of_view = pov
        self._restore_position()
        # We connect the post move signal here to not store the potentially restored position unnecessarily
        entity_post_move.connect(self._save_location)
        entity_rotated.connect(self._save_location)

    def _restore_position(self):
        self.restored_position = False
        last = map().last_location
        if last:
            self._point_of_view.move_to(last[0], force=True)
            self._point_of_view.set_direction(last[1])
            self.restored_position = True
        
    def _save_location(self, sender):
        if sender is self._point_of_view:
            map().last_location = (sender.position, sender.direction)

    def reset(self, person):
        self._point_of_view = person
        self._restore_position()