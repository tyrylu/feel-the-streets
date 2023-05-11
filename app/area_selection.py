import logging
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLabel, QMessageBox, QInputDialog, QDialog, QTreeWidgetItem
from .base_dialog import BaseDialog
from .server_interaction import has_api_connectivity, get_areas, request_area_creation, get_osm_object_names
from .time_utils import rfc_3339_to_local_string
from .size_utils import format_size
from .areas_browser import AreasBrowserDialog
from.area_candidates_searcher import AreaCandidatesSearcher
from .search_indicator import SearchIndicator
from .local_utils import get_local_area_ids
from .more_accessible_tree_widget import MoreAccessibleTreeWidget
from .services import config

def area_id_to_osm_id(area_id):
    return f"r{area_id - 3600000000}"

def translate_area_state(state):
    translations = {"Updated": _("updated"), "Creating": _("creating"), "GettingChanges": _("getting changes"), "ApplyingChanges": _("applying changes"), "Frozen": _("frozen"), "LocalCopyExists": _("local copy exists"), "Local": _("local")}
    return ", ".join(translations[s] for s in state.split(","))

def mark_areas_as_also_local(areas):
    local_ids = get_local_area_ids()
    for area in areas:
        if area["osm_id"] in local_ids:
            area["state"] += ",LocalCopyExists"

def osm_object_id_to_name(osm_object_id, osm_object_names):
    if osm_object_id not in osm_object_names:
        return _("Unknown area {}").format(osm_object_id)
    lang = os.environ["LANG"]
    if "_" in lang:
        lang = lang.split("_")[0]
    return osm_object_names[osm_object_id].get(lang, osm_object_names[osm_object_id]["native"])

log = logging.getLogger(__name__)

class AreaSelectionDialog(BaseDialog):
    def __init__(self, parent, is_initial):
        if is_initial:
            close_label = _("&Exit")
        else:
            close_label = _("&Close")
        super().__init__(parent, _("Select an area"), _("&Select"), close_label, cancel_button_column=2, buttons_to_new_row=False)
        self._initialize_areas()
        
    def _initialize_areas(self):
        available = get_areas()
        if has_api_connectivity():
            mark_areas_as_also_local(available)
        else:
            self.request_button.setDisabled(True)
        self._osm_object_items = {}
        self._osm_object_names = get_osm_object_names()
        self._fill_areas(available)
        self._areas.setSortingEnabled(True)
        self._areas.sortByColumn(0, Qt.AscendingOrder)
        self._areas.setFocus()

    def create_ui(self):
        areas_label = QLabel(_("&Available areas"))
        self.layout.addWidget(areas_label, 0, 0, 1, 3)
        self._areas = MoreAccessibleTreeWidget()
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
            area["state"] = translate_area_state(area["state"])
            try:
                area["name"] = osm_object_id_to_name(area_id_to_osm_id(area["osm_id"]), self._osm_object_names)
            except KeyError:
                pass
            parents = area["parent_osm_ids"].split(",")
            target_id = self._ensure_parents(parents)
            item = QTreeWidgetItem([_("{name}: {state}, last updated {updated_at}, file size {db_size}, created {created_at}").format(**area)])
            item.setData(0, Qt.UserRole, area)
            if target_id:
                self._osm_object_items[target_id].addChild(item)
            else:
                self._areas.addTopLevelItem(item)

    def _ensure_parents(self, parents):
        target_id = None
        for idx, parent in enumerate(parents[:-1]):
            if idx + 1 > config().presentation.areas_list_max_parents: break
            target_id = parent
            if parent in self._osm_object_items: continue
            item = QTreeWidgetItem([osm_object_id_to_name(parent, self._osm_object_names)])
            self._osm_object_items[parent] = item
            if idx == 0:
                self._areas.addTopLevelItem(item)
            else:
                self._osm_object_items[parents[idx - 1]].addChild(item)
        return target_id

    @property
    def selected_map(self):
        return self._areas.currentItem().data(0, Qt.UserRole)["osm_id"]

    @property
    def selected_map_name(self):
        return self._areas.currentItem().data(0, Qt.UserRole)["name"]

    def on_request_clicked(self):
        name, ok = QInputDialog.getText(self, _("Enter the name of the requested area"), _("Area name requested"))
        if not ok or not name:
            return
        self._searched_name = name
        self._searcher = AreaCandidatesSearcher(name)
        self._searcher.results_ready.connect(self._on_area_candidates)
        self._searcher.rate_limited.connect(self._on_rate_limited)
        self._indicator = SearchIndicator()
        self._indicator.show()
        self._searcher.start()
    
    def _on_rate_limited(self):
        self._indicator.hide()
        QMessageBox.warning(self, _("Query limit reached"), _("You've reached the query limit for the overpass API, which is used for area searches. Try to request the area in a few minutes."))


    def _on_area_candidates(self, candidates):
        self._indicator.hide()
        if not candidates:
            QMessageBox.warning(self, _("Area not found"), _("The area with name {name} does not correspond to any OSM areas.").format(name=self._searched_name))
            return
        if len(candidates) == 1:
            area_id = next(iter(candidates.keys()))
            log.info("Only one candidate with an admin level of %s and id %s.", next(iter(candidates.values()))[1]["admin_level"], area_id)
        else:
            dialog = AreasBrowserDialog(self, area_name=self._searched_name, areas=candidates)
            res = dialog.exec_()
            if res == QDialog.DialogCode.Accepted:
                area_id = dialog.selected_area_id
            else:
                return
        reply = request_area_creation(area_id, self._searched_name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            QMessageBox.information(self, _("Success"), _("The area creation request has been sent successfully. The area will become updated in a few minutes."))
            self._areas.clear()
            self._initialize_areas()
        elif reply and isinstance(reply, dict) and "state" in reply and reply["state"] in {"Creating", "Updated", "ApplyingChanges", "GettingChanges"}:
            QMessageBox.information(self, _("Success"), _("The area creation request has already been sent."))
        else:
            QMessageBox.warning(self, text=_("The area creation request failed. Response from server: {reply}").format(reply=reply), title=_("Failure"))