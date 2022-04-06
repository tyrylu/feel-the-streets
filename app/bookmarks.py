from PySide6.QtWidgets import QListWidget
from pygeodesy.ellipsoidalVincenty import LatLon
from .base_dialog import BaseDialog
from .geometry_utils import distance_between, bearing_to
from .humanization_utils import format_number
from .services import config

class BookmarksDialog(BaseDialog):
    def __init__(self, parent, bookmarks, pov):
        super().__init__(parent, _("Bookmarks"), _("&Go to bookmark"), _("&Close"))
        self._bookmarks = bookmarks
        print(bookmarks)
        for mark in self._bookmarks:
            point = LatLon(mark.latitude, mark.longitude)
            dist = format_number(distance_between(pov.position, point), config().presentation.distance_decimal_places)
            bearing = format_number((bearing_to(pov.position, point) - pov.direction) % 360, config().presentation.angle_decimal_places)
            self._bookmarks_list.addItem(_("{name}: distance {distance} meters, {bearing}° relatively").format(name=mark.name, distance=dist, bearing=bearing))
        
    def create_ui(self):
        self._bookmarks_list = QListWidget(self)
        self.layout.addWidget(self._bookmarks_list, 0, 0)

    @property
    def selected_bookmark(self):
        return self._bookmarks[self._bookmarks_list.currentRow()]