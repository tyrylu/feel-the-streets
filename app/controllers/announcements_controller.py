from ..services import speech
from ..entities import entity_post_enter, entity_post_leave

class AnnouncementsController:
    def __init__(self, pov):
        self._point_of_view = pov
        entity_post_enter.connect(self._on_post_enter)
        entity_post_leave.connect(self._on_post_leave)
    
    def _on_post_enter(self, sender, enters):
        if sender is self._point_of_view:
            speech().speak("Vstupujete do %s."%enters)
            
    def _on_post_leave(self, sender, leaves):
        if sender is self._point_of_view:
            speech().speak("Opouštíte %s."%leaves)
