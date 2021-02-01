import logging
from PySide2.QtCore import QThread, Signal
from .server_interaction import get_areas_with_name, get_area_parents

log = logging.getLogger(__name__)

class AreaCandidatesSearcher(QThread):
    results_ready = Signal(dict)

    def __init__(self, area_name):
        super().__init__()
        self._area_name = area_name
    
    def run(self):
        raw_candidates = get_areas_with_name(self._area_name)
        candidates = {}
        for id, data in raw_candidates.items():
            parents = get_area_parents(id)
            if len(parents) > 1:
                log.warning("Area with id %s has multiple parents, falling back on the first.", id)
            if parents:
                parent_name = next(iter(parents.values()))["name"]
            else:
                parent_name = _("not known")
            candidates[id] = (parent_name, data)
        self.results_ready.emit(candidates)
            
