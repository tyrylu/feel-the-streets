import glob
import logging
import os
from PySide2.QtWidgets import QPushButton, QListWidget, QLabel, QMessageBox, QInputDialog, QDialog
import pendulum
from osm_db import AreaDatabase
from .base_dialog import BaseDialog
from .server_interaction import has_api_connectivity, get_areas, request_area_creation
from .time_utils import rfc_3339_to_local_string
from .size_utils import format_size
from .areas_browser import AreasBrowserDialog
from .services import config
from.area_candidates_searcher import AreaCandidatesSearcher
from .search_indicator import SearchIndicator

log = logging.getLogger(__name__)

def cache_area_names(areas_response):
    with open(os.path.join(config().config_path, "area.names"), "w", encoding="utf-8") as fp:
        for area in areas_response:
            fp.write("{}={}\n".format(area["osm_id"], area["name"]))

def get_area_names_cache():
    names = {}
    cache_path = os.path.join(config().config_path, "area.names")
    if not os.path.exists(cache_path):
        return names
    with open(cache_path, encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            parts = line.split("=")
            names[int(parts[0])] = parts[1]
    return names

def get_local_area_infos():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for(12345, False))
    cache = get_area_names_cache()
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        info = os.stat(db_file)
        osm_id = int(os.path.basename(db_file).replace(".db", ""))
        name = cache.get(osm_id, str(osm_id))
        mtime = pendulum.from_timestamp(info.st_mtime).to_rfc3339_string()
        ctime = pendulum.from_timestamp(info.st_ctime).to_rfc3339_string()
        results.append({"osm_id": osm_id, "name":name, "updated_at": mtime, "state": "local", "created_at": ctime, "db_size": info.st_size})
    return results

class AreaSelectionDialog(BaseDialog):
    def __init__(self, parent):
        super().__init__(parent, _("Select an area"), _("&Select"), _("&Exit"), cancel_button_column=2, buttons_to_new_row=False)
        if has_api_connectivity():
            available = get_areas()
            cache_area_names(available)
        else:
            available = get_local_area_infos()
            self.request_button.setDisabled(True)
        self._area_ids = [a["osm_id"] for a in available]
        self._area_names = [a["name"] for a in available]
        self._fill_areas(available)

    def create_ui(self):
        areas_label = QLabel(_("&Available areas"))
        self.layout.addWidget(areas_label, 0, 0, 1, 3)
        self._areas = QListWidget()
        self._areas.setAccessibleName(_("Available areas"))
        self.layout.addWidget(self._areas, 1, 0, 1, 3)
        areas_label.setBuddy(self._areas)
        self.request_button = QPushButton(_("&Request a new area"))
        self.layout.addWidget(self.request_button, 2, 1)
        self.request_button.clicked.connect(self.on_request_clicked)

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
        self._searched_name = name
        self._searcher = AreaCandidatesSearcher(name)
        self._searcher.results_ready.connect(self._on_area_candidates)
        self._indicator = SearchIndicator()
        self._indicator.show()
        self._searcher.start()
    
    def _on_area_candidates(self, candidates):
        self._indicator.hide()
        if not candidates:
            QMessageBox.warning(self, _("Area not found"), _("The area with name {name} does not correspond to any OSM areas.").format(name=name))
            return
        if len(candidates) == 1:
            area_id = next(iter(candidates.keys()))
            log.info("Only one candidate with an admin level of %s and id %s.", next(iter(candidates.values()))["admin_level"], area_id)
        else:
            dialog = AreasBrowserDialog(self, area_name=self._searched_name, areas=candidates)
            res = dialog.exec_()
            if res == QDialog.DialogCode.Accepted:
                area_id = dialog.selected_area_id
            else:
                return
        reply = request_area_creation(area_id, name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            QMessageBox.information(self, _("Success"), _("The area creation request has been sent successfully. The area will become updated in a few minutes."))
        elif reply and isinstance(reply, dict) and "state" in reply and reply["state"] in {"Creating", "Updated", "ApplyingChanges", "GettingChanges"}:
            QMessageBox.information(self, _("Success"), _("The area creation request has already been sent."))
        else:
            QMessageBox.warning(self, text=_("The area creation request failed. Response from server: {reply}").format(reply=reply), title=_("Failure"))