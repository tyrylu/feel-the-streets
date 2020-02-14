import logging
from PySide2.QtWidgets import QMainWindow, QDialog, QProgressDialog, QApplication, QMessageBox, QWidget
import os
import json
import datetime
import webbrowser
from pygeodesy.ellipsoidalVincenty import LatLon
import bitmath
import shapely.wkb as wkb
from shapely.geometry.linestring import LineString
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController, LastLocationController
from .area_selection import AreaSelectionDialog
from .services import map, menu_service
from .server_interaction import download_area_database, SemanticChangeRetriever, has_api_connectivity
from .semantic_changelog_generator import get_change_description
from osm_db import AreaDatabase, EntitiesQuery, CHANGE_REMOVE
from uimanager import get

log = logging.getLogger(__name__)

def format_size(num_bytes):
    size = bitmath.Byte(num_bytes)
    return size.best_prefix().format("{value:.2f} {unit}")

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("Feel the streets")
        self.setCentralWidget(QWidget(self))
        self._download_progress_dialog = None
        dlg = AreaSelectionDialog(self)
        res = dlg.exec_()        
        if res == QDialog.DialogCode.Rejected:
            self.close()
            return
        elif res == QDialog.DialogCode.Accepted:
            if not os.path.exists(AreaDatabase.path_for(dlg.selected_map, server_side=False)):
                self._download_database(dlg.selected_map)
            else:
                self._update_database(dlg.selected_map)
            map.set_call_args(dlg.selected_map)
            menu_service.set_call_args(self.menuBar())
        self._app_controller = ApplicationController(self)
        person = Person(map(), LatLon(0, 0))
        self._person_controller = InteractivePersonController(person, self)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        self._last_location_controller = LastLocationController(person)
        if not self._last_location_controller.restored_position:
            query = EntitiesQuery()
            query.set_limit(1)
            entity = map()._db.get_entities(query)[0]
            geom = wkb.loads(entity.geometry)
            if isinstance(geom, LineString):
                geom = geom.representative_point()
            lon = geom.x
            lat = geom.y
            person.move_to(LatLon(lat, lon))

   
    def _download_progress_callback(self, total, so_far):
        if not self._download_progress_dialog:
            self._download_progress_dialog = QProgressDialog(_("Downloading the selected database."), "", 0, 100, self)
            self._download_progress_dialog.setWindowTitle(_("Download in progress"))
        percentage = int((so_far/total)*100)
        self._download_progress_dialog.setLabelText(_("Downloading the selected database. Downloaded {so_far} of {total}.").format(so_far=format_size(so_far), total=format_size(total)))
        self._download_progress_dialog.setValue(percentage)
        QApplication.instance().processEvents()

    def _download_database(self, area):
        res = download_area_database(area, self._download_progress_callback)
        if not res:
            QMessageBox.warning(self, _("Download failure"), _("Download of the selected area had failed."))
            self.Close()
            os.remove(AreaDatabase.path_for(area, server_side=False))
            return


    def _update_database(self, area):
        if not has_api_connectivity():
            return
        retriever = SemanticChangeRetriever()
        pending_count = retriever.new_change_count_in(area)
        if not pending_count:
            return
        db = AreaDatabase.open_existing(area, server_side=False)
        generate_changelog = True
        if pending_count > 10000:
            resp = QMessageBox.question(self, _("Question"), _("The server reports %s pending changes. Do you really want to generate the changelog from all of them? It might take a while.")%pending_count)
            if resp == QMessageBox.StandardButton.Yes:
                generate_changelog = False
        db.begin()
        progress = QProgressDialog(_("Applying changes for the selected database."), "", 0, pending_count, self)
        progress.setWindowTitle(_("Change application"))
        changelog_path = os.path.join(os.path.dirname(AreaDatabase.path_for(12345, server_side=False)), "..", "changelogs", "{0}_{1}.txt".format(area, datetime.datetime.now().isoformat().replace(":", "_")))
        os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
        changelog = open(changelog_path, "w", encoding="UTF-8")
        for nth, change in enumerate(retriever.new_changes_in(area)):
            progress.setLabelText(_("Applying changes for the selected database, change {nth} of {total}").format(nth=nth, total=pending_count))
            progress.setValue(nth)
            QApplication.instance().processEvents()
            entity = None
            if generate_changelog and change.type is CHANGE_REMOVE:
                entity= db.get_entity(change.osm_id)
            db.apply_change(change)
            QApplication.instance().processEvents()
            if generate_changelog:
                if not entity:
                    if change.osm_id:
                        entity = db.get_entity(change.osm_id)
                        if not entity:
                            log.error("Local database is missing entity with osm id %s, not generating changelog description for that one.", change.osm_id)
                            continue
                    else:
                        # This is somewhat ugly, but we really don't have the entity id in any other place and we need its discriminator.
                        data = [c.new_value for c in change.property_changes if c.key == "data"][0]
                        entity = db.get_entity(json.loads(data)["osm_id"])
                        if not entity:
                            log.error("No entity for osm id %s.", data["osm_id"])
                            continue
                changelog.write(get_change_description(change, entity))
        db.commit()
        changelog.close()
        retriever.acknowledge_changes_for(area)
        changelog_size = os.path.getsize(changelog_path)
        resp = QMessageBox.question(self, _("Success"), _("Successfully applied {total} changes. A changelog of size {size} was generated, do you want to view it now?").format(total=pending_count, size=format_size(changelog_size)))
        if resp == QMessageBox.StandardButton.Yes:
            # Somewhat hacky, but os.startfile is not cross platform and the webbrowser way appears to be.
            webbrowser.open(changelog_path)

