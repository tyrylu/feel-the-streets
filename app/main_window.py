import sys
from PySide2.QtWidgets import QMainWindow, QDialog, QProgressDialog, QMessageBox, QWidget
import os
import webbrowser
from pygeodesy.ellipsoidalVincenty import LatLon
import bitmath
import shapely.wkb as wkb
from shapely.geometry.linestring import LineString
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController, LastLocationController
from .area_selection import AreaSelectionDialog
from .services import map, menu_service
from .server_interaction import AreaDatabaseDownloader, SemanticChangeRetriever, has_api_connectivity
from .changes_applier import ChangesApplier
from osm_db import AreaDatabase, EntitiesQuery

def format_size(num_bytes):
    size = bitmath.Byte(num_bytes)
    return size.best_prefix().format("{value:.2f} {unit}")

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("Feel the streets")
        self.setCentralWidget(QWidget(self))
        self._download_progress_dialog = None
        self._downloader = None
        self._progress = None
        self._pending_count = 0
        self._applier = None
        self._do_select_db()

    def _do_select_db(self):
        dlg = AreaSelectionDialog(self)
        res = dlg.exec_()        
        if res == QDialog.DialogCode.Rejected:
            sys.exit(0)
        elif res == QDialog.DialogCode.Accepted:
            self._selected_map = dlg.selected_map
            if not os.path.exists(AreaDatabase.path_for(dlg.selected_map, server_side=False)):
                self._download_database(dlg.selected_map)
            else:
                self._update_database(dlg.selected_map)

    def _on_map_ready(self):
        map.set_call_args(self._selected_map)
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
        self.show()

   
    def _download_progress_callback(self, total, so_far):
        if not self._download_progress_dialog:
            self._download_progress_dialog = QProgressDialog(_("Downloading the selected database."), "", 0, 100, self)
            self._download_progress_dialog.setWindowTitle(_("Download in progress"))
        percentage = int((so_far/total)*100)
        self._download_progress_dialog.setLabelText(_("Downloading the selected database. Downloaded {so_far} of {total}.").format(so_far=format_size(so_far), total=format_size(total)))
        self._download_progress_dialog.setValue(percentage)

    def _download_database(self, area):
        self._downloader = AreaDatabaseDownloader(area, self)
        self._downloader.download_progressed.connect(self._download_progress_callback)
        self._downloader.download_finished.connect(self._on_download_finished)
        self._downloader.start()
    
    def _on_download_finished(self, res):
        if not res:
            QMessageBox.warning(self, _("Download failure"), _("Download of the selected area had failed."))
            self.Close()
            os.remove(AreaDatabase.path_for(area, server_side=False))
        else:
            self._on_map_ready()


    def _update_database(self, area):
        if not has_api_connectivity():
            self._on_map_ready()
            return
        retriever = SemanticChangeRetriever()
        self._pending_count = retriever.new_change_count_in(area)
        if not self._pending_count:
            self._on_map_ready()
            return
        generate_changelog = True
        if self._pending_count > 10000:
            resp = QMessageBox.question(self, _("Question"), _("The server reports %s pending changes. Do you really want to generate the changelog from all of them? It might take a while.")%self._pending_count)
            if resp == QMessageBox.StandardButton.Yes:
                generate_changelog = False
        self._progress = QProgressDialog(_("Applying changes for the selected database."), "", 0, self._pending_count, self)
        self._progress.setWindowTitle(_("Change application"))
        self._applier = ChangesApplier(area, retriever, generate_changelog)
        self._applier.will_process_change.connect(self._on_will_process_change)
        self._applier.changes_applied.connect(self._on_changes_applied)
        self._applier.start()
        
        
    def _on_will_process_change(self, nth):
        self._progress.setLabelText(_("Applying changes for the selected database, change {nth} of {total}").format(nth=nth, total=self._pending_count))
        self._progress.setValue(nth)
            
    def _on_changes_applied(self, changelog_path):
        changelog_size = os.path.getsize(changelog_path)
        resp = QMessageBox.question(self, _("Success"), _("Successfully applied {total} changes. A changelog of size {size} was generated, do you want to view it now?").format(total=self._pending_count, size=format_size(changelog_size)))
        if resp == QMessageBox.StandardButton.Yes:
            # Somewhat hacky, but os.startfile is not cross platform and the webbrowser way appears to be.
            webbrowser.open(changelog_path)
        self._on_map_ready()

