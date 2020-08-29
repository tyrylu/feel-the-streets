import sys
from PySide2.QtWidgets import QMainWindow, QDialog, QProgressDialog, QMessageBox, QWidget, QApplication
import os
import webbrowser
from pygeodesy.ellipsoidalVincenty import LatLon
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController, LastLocationController, MovementRestrictionController, InterestingEntitiesController
from .area_selection import AreaSelectionDialog
from .services import map, menu_service, config
from .server_interaction import AreaDatabaseDownloader, SemanticChangeRetriever, has_api_connectivity, ConnectionError, UnknownQueueError
from .changes_applier import ChangesApplier
from osm_db import AreaDatabase, EntitiesQuery
from .size_utils import format_size


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
            self._selected_map_name = dlg.selected_map_name
            if not os.path.exists(AreaDatabase.path_for(dlg.selected_map, server_side=False)):
                self._download_database(dlg.selected_map)
            else:
                self._update_database(dlg.selected_map)

    def _on_map_ready(self):
        map.set_call_args(self._selected_map, self._selected_map_name)
        menu_service.set_call_args(self)
        self._app_controller = ApplicationController(self)
        person = Person(map=map(), position=LatLon(0, 0))
        self._person_controller = InteractivePersonController(person, self)
        self._interesting_entities_controller = InterestingEntitiesController(person)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        self._last_location_controller = LastLocationController(person)
        self._restriction_controller = MovementRestrictionController(person)
        if not self._last_location_controller.restored_position:
                  person.move_to(map().default_start_location)
        self.raise_()
        menu_service().ensure_key_capturer_focus()


    def _download_progress_callback(self, total, so_far):
        if not self._download_progress_dialog:
            self._download_progress_dialog = QProgressDialog(_("Downloading the selected database."), None, 0, 100, self)
            self._download_progress_dialog.setWindowTitle(_("Download in progress"))
        percentage = int((so_far/total)*100)
        self._download_progress_dialog.setLabelText(_("Downloading the selected database. Downloaded {so_far} of {total}.").format(so_far=format_size(so_far), total=format_size(total)))
        self._download_progress_dialog.setValue(percentage)

    def _download_database(self, area):
        self._downloader = AreaDatabaseDownloader(area, None)
        self._downloader.moveToThread(QApplication.instance().thread())
        self._downloader.download_progressed.connect(self._download_progress_callback)
        self._downloader.download_finished.connect(self._on_download_finished)
        self._downloader.start()

    def _on_download_finished(self, res):
        if not res:
            QMessageBox.warning(self, _("Download failure"), _("Download of the selected area had failed."))
            self.close()
            os.remove(AreaDatabase.path_for(area, server_side=False))
        else:
            self._on_map_ready()


    def _update_database(self, area):
        if not has_api_connectivity():
            self._on_map_ready()
            return
        try:
            retriever = SemanticChangeRetriever()
            self._pending_count = retriever.new_change_count_in(area)
        except ConnectionError:
            QMessageBox.warning(self, _("Warning"), _("Could not retrieve changes in the selected area, using the potentially stale local copy."))
            self._on_map_ready()
            return
        except UnknownQueueError:
            QMessageBox.warning(self, _("Warning"), _("The changes queue for the selected database no longer exists on the server, downloading it as if it was a new area."))
            self._download_database(area)
            return
        if not self._pending_count:
            self._on_map_ready()
            return
        generate_changelog = config().changelogs.enabled
        if self._pending_count > 10000 and generate_changelog:
            resp = QMessageBox.question(self, _("Question"), _("The server reports %s pending changes. Do you really want to generate the changelog from all of them? It might take a while.")%self._pending_count)
            if resp == QMessageBox.StandardButton.Yes:
                generate_changelog = False
        self._progress = QProgressDialog(_("Applying changes for the selected database."), None, 0, self._pending_count, self)
        self._progress.setWindowTitle(_("Change application"))
        self._applier = ChangesApplier(area, retriever, generate_changelog)
        self._applier.will_process_change.connect(self._on_will_process_change)
        self._applier.changes_applied.connect(self._on_changes_applied)
        self._applier.redownload_requested.connect(self._on_redownload_requested)
        self._applier.start()
        
    def _on_redownload_requested(self):
        self._progress.close()
        self._progress = None
        QMessageBox.information(self, _("Redownload requested"), _("The server has requested a redownload of the selected database, proceeding with the operation."))
        self._download_database(self._selected_map)
        
    def _on_will_process_change(self, nth):
        self._progress.setLabelText(_("Applying changes for the selected database, change {nth} of {total}").format(nth=nth, total=self._pending_count))
        self._progress.setValue(nth)
            
    def _on_changes_applied(self, changelog_path):
        self._applier.deleteLater()
        if changelog_path:
            changelog_size = os.path.getsize(changelog_path)
            resp = QMessageBox.question(self, _("Success"), _("Successfully applied {total} changes. A changelog of size {size} was generated, do you want to view it now?").format(total=self._pending_count, size=format_size(changelog_size)), defaultButton=QMessageBox.No)
            if resp == QMessageBox.StandardButton.Yes:
                # Somewhat hacky, but os.startfile is not cross platform and the webbrowser way appears to be.
                webbrowser.open(changelog_path)
        else:
            QMessageBox.information(self, _("Success"), _("Successfully applied {total} changes.").format(total=self._pending_count))
        self._on_map_ready()

