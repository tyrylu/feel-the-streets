from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication
from ..services import map
from ..geometry_utils import distance_filter

class QueryExecutor(QThread):
    results_ready = Signal(list)

    def __init__(self, query, position, distance):
        super().__init__()
        self._query = query
        self._position = position
        self._distance = distance

    def run(self):
        results = map().get_entities(self._query)
        filtered_objects = distance_filter(results, self._position, self._distance)
        self.results_ready.emit(filtered_objects)
