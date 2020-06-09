import glob
import logging
import os
from PySide2.QtWidgets import QDialog, QGridLayout, QPushButton, QListWidget, QLabel, QMessageBox, QInputDialog
import pendulum
from .server_interaction import has_api_connectivity, get_areas, request_area_creation, get_areas_with_name
from .time_utils import rfc_3339_to_local_string
from .size_utils import format_size
from .areas_browser import AreasBrowserDialog
from osm_db import AreaDatabase

log = logging.getLogger(__name__)


def get_local_area_infos():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for(12345, False))
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        info = os.stat(db_file)
        name = os.path.basename(db_file).replace(".db", "")
        mtime = pendulum.from_timestamp(info.st_mtime).to_rfc3339_string()
        ctime = pendulum.from_timestamp(info.st_ctime).to_rfc3339_string()
        # Cache names for offline use, they're ugly now.
        results.append({"osm_id": int(name), "name":name, "updated_at": mtime, "state": "local", "created_at": ctime, "db_size": info.st_size})
    return results


class AreaSelectionDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(_("Select an area"))
        layout = QGridLayout(self)
        areas_label = QLabel(_("&Available areas"))
        layout.addWidget(areas_label, 0, 0, 1, 3)
        self._areas = QListWidget()
        self._areas.setAccessibleName(_("Available areas"))
        layout.addWidget(self._areas, 1, 0, 1, 3)
        areas_label.setBuddy(self._areas)
        select_button = QPushButton(_("&Select"))
        layout.addWidget(select_button, 2, 0)
        select_button.setDefault(True)
        select_button.clicked.connect(self.accept)
        request_button = QPushButton(_("&Request a new area"))
        layout.addWidget(request_button, 2, 1)
        request_button.clicked.connect(self.on_request_clicked)
        exit_button = QPushButton(_("&Exit"))
        layout.addWidget(exit_button, 2, 2)
        exit_button.clicked.connect(self.reject)
        self.setLayout(layout)
        if has_api_connectivity():
            available = get_areas()
        else:
            available = get_local_area_infos()
            request_button.setDisabled(True)
        self._area_ids = [a["osm_id"] for a in available]
        self._area_names = [a["name"] for a in available]
        self._fill_areas(available)

    def _fill_areas(self, areas):
        for area in areas:
            area["created_at"] = rfc_3339_to_local_string(area["created_at"])
            area["updated_at"] = rfc_3339_to_local_string(area["updated_at"])
            area["db_size"] = format_size(area["db_size"])
            self._areas.addItem(_("{name}: {state}, last updated {updated_at}, file size {db_size}, created {created_at}").format(**area))
    
    @property
    def selected_map(self):
        return self._area_ids[self._areas.currentRow()]
    
    @property
    def selected_map_name(self):
        return self._area_names[self._areas.currentRow()]
    

    def on_request_clicked(self):
        name, ok = QInputDialog.getText(self, _("Enter the name of the requested area"), _("Area name requested"))
        if not ok or not name:
            return
        candidates = get_areas_with_name(name)
        if not candidates:
            QMessageBox.warning(self, text=_("The area with name {name} does not correspond to any OSM areas.").format(name=name), title=_("Area not found"))
            return
        if len(candidates) == 1:
            area_id = next(iter(candidates.keys()))
            log.info("Only one candidate with an admin level of %s and id %s.", next(iter(candidates.values()))["admin_level"], area_id)
        else:
            dialog = AreasBrowserDialog(self, areas=candidates)
            res = dialog.exec_()
            if res == QDialog.DialogCode.Accepted:
                area_id = dialog.selected_area_id
            else:
                return
        reply = request_area_creation(area_id, name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            QMessageBox.information(self, message=_("The area creation request has been sent successfully. The area will become updated in a few minutes."), title=_("Success"))
        elif reply and isinstance(reply, dict) and "state" in reply and reply["state"] in {"Creating", "Updated", "ApplyingChanges", "GettingChanges"}:
            QMessageBox.information(self, text=_("The area creation request has already been sent."), title=_("Success"))
        else:
            QMessageBox.warning(self, text=_("The area creation request failed. Response from server: {reply}").format(reply=reply), title=_("Failure"))