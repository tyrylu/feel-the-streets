from PySide6.QtCore import QThread, Signal

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
        