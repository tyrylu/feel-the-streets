from ..entities import entity_post_move
from ..services import map

class LastLocationController:

    def __init__(self, pov):
        self._point_of_view = pov
        self.restored_position = False
        last = map().last_location
        if last:
            self._point_of_view.move_to(last)
            self.restored_position = True
        # We connect the post move signal here to not store the potentially restored position unnecessarily
        entity_post_move.connect(self._on_post_move)

    def             _on_post_move(self, sender):
        if sender is self._point_of_view:
            map().last_location = sender.position