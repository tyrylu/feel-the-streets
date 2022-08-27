from PySide6.QtWidgets import QListWidget, QPushButton, QMessageBox, QInputDialog
from pygeodesy.ellipsoidalVincenty import LatLon
from .base_dialog import BaseDialog
from .geometry_utils import distance_between, bearing_to
from .humanization_utils import format_number
from .services import config, map, app_db

def get_bookmark_name(parent, default=""):
    while True:
        name, ok = QInputDialog.getText(parent, _("Data entry"), _("Enter a name for the bookmark"), text=default)
        if not ok or not name:
            return None
        if name.startswith("."):
            QMessageBox.warning(self._main_window, _("Error"), _("The bookmark name can not start with a dot, please enter a different name."))
        else:
            return name

class BookmarksDialog(BaseDialog):
    def __init__(self, parent, bookmarks, pov):
        super().__init__(parent, _("Bookmarks"), _("&Go to bookmark"), _("&Close"))
        self._bookmarks = bookmarks
        for mark in self._bookmarks:
            point = LatLon(mark.latitude, mark.longitude)
            dist = format_number(distance_between(pov.position, point), config().presentation.distance_decimal_places)
            bearing = format_number((bearing_to(pov.position, point) - pov.direction) % 360, config().presentation.angle_decimal_places)
            self._bookmarks_list.addItem(_("{name}: distance {distance} meters, {bearing}° relatively").format(name=mark.name, distance=dist, bearing=bearing))
        
    def create_ui(self):
        self._bookmarks_list = QListWidget(self)
        self._rename_button = QPushButton(_("&Rename"), self)
        self._rename_button.clicked.connect(self._on_rename_clicked)
        self._delete_button = QPushButton(_("&Delete"), self)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        self.layout.addWidget(self._rename_button, 1, 0)
        self.layout.addWidget(self._delete_button, 1, 1)
        self.layout.addWidget(self._bookmarks_list, 0, 0, 0, 2)

    @property
    def selected_bookmark(self):
        return self._bookmarks[self._bookmarks_list.currentRow()]

    def _on_delete_clicked(self):
        mark = self.selected_bookmark
        if QMessageBox.question(self, _("Question"), _("Do you really want to delete the bookmark {name}?").format(name=mark.name)) == QMessageBox.Yes:
            self._bookmarks.remove(mark)
            self._bookmarks_list.takeItem(self._bookmarks_list.currentRow())
            map().remove_bookmark(mark)

    def _on_rename_clicked(self):
        mark = self.selected_bookmark
        old_name = mark.name
        new_name = get_bookmark_name(self, mark.name)
        if not new_name:
            return
        mark.name = new_name
        item = self._bookmarks_list.currentItem()
        item.setText(item.text().replace(old_name, new_name))
        app_db().update_bookmark(mark)