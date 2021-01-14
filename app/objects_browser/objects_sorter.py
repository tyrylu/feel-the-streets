from PySide2.QtCore import QThread, Signal
from ..services import config
from ..humanization_utils import format_number, describe_entity
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
        objects = []
        items_data = []
        for obj in self._unsorted_objects:
            closest_latlon = self._person.closest_point_to(obj.geometry)
            cur_distance = distance_between(closest_latlon, self._person.position)
            objects.append((cur_distance, obj, closest_latlon))
        objects.sort(key=lambda e: e[0])
        for dist, obj, closest in objects:
            bearing = bearing_to(self._person.position, closest)
            rel_bearing = (bearing - self._person.direction) % 360
            rel_bearing = format_number(rel_bearing, config().presentation.angle_decimal_places)
            dist = format_number(dist, config().presentation.distance_decimal_places)
            items_data.append((describe_entity(obj), dist, rel_bearing))
        return objects, items_data
        