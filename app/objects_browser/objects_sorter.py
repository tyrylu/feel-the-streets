from PySide6.QtCore import QThread, Signal
from ..services import config
from ..humanization_utils import format_number, format_rel_bearing, describe_entity
from ..geometry_utils import distance_between, bearing_to


class ObjectsSorter(QThread):
    objects_sorted = Signal(tuple)

    def __init__(self, unsorted_objects, person):
        super().__init__(None)
        self._unsorted_objects = unsorted_objects
        self._person = person

    def run(self):
        self.objects_sorted.emit(self.perform_sorting())
    
    def perform_sorting(self):
        rels = [self._person.spatial_relationship_to(o) for o in self._unsorted_objects]
        rels.sort(key=lambda r: r.distance)
        return rels
        