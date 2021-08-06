import sys
from PySide2.QtWidgets import QMainWindow, QDialog, QProgressDialog, QMessageBox, QWidget, QApplication
import os
import webbrowser
from pygeodesy.ellipsoidalVincenty import LatLon
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController, LastLocationController, MovementRestrictionController, InterestingEntitiesController, SpeechController, PositionAdjustmentController
from .area_selection import AreaSelectionDialog
from .services import map, menu_service, config
from .server_interaction import AreaDatabaseDownloader, SemanticChangeRetriever, has_api_connectivity, ConnectionError, get_motd, create_client
from .changes_applier import ChangesApplier
from .message_dialog import MessageDialog
from .local_areas_utils import get_area_names_cache
from osm_db import AreaDatabase, EntitiesQuery
from .size_utils import format_size

FROZEN_AREA_OSM_ID_OFFSET = 20000000000

def is_frozen_area(area_id):
    return area_id > FROZEN_AREA_OSM_ID_OFFSET

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
        self._maybe_show_message()
        self._do_select_db()

    def _maybe_show_message(self):
        motd = get_motd()
        if motd and motd.is_newer_than_last_local:
            message_dialog = MessageDialog(self, motd)
            res = message_dialog.exec_()
            if res == MessageDialog.DialogCode.Rejected:
                sys.exit(0)
            elif res == MessageDialog.DialogCode.Accepted:
                motd.mark_as_seen()


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
        self.setWindowTitle(f"{self._selected_map_name} - Feel the streets")
        if is_frozen_area(self._selected_map):
            original_id = self._selected_map - FROZEN_AREA_OSM_ID_OFFSET
            area_name = get_area_names_cache()[original_id]
        else:
            area_name = self._selected_map_name
        map.set_call_args(self._selected_map, area_name)
        menu_service.set_call_args(self)
        self._app_controller = ApplicationController(self)
        person = Person(map=map(), position=LatLon(0, 0))
        self._person_controller = InteractivePersonController(person, self)
        self._interesting_entities_controller = InterestingEntitiesController(person)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        self._last_location_controller = LastLocationController(person)
        self._restriction_controller = MovementRestrictionController(person)
        self._speech_controller = SpeechController()
        self._adjustment_controller = PositionAdjustmentController(person)
        if not self._last_location_controller.restored_position:
                  person.move_to(map().default_start_location, force=True)
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
        self._area = area
        self._downloader.moveToThread(QApplication.instance().thread())
        self._downloader.download_progressed.connect(self._download_progress_callback)
        self._downloader.download_finished.connect(self._on_download_finished)
        self._downloader.start()

    def _on_download_finished(self, res):
        if not res:
            QMessageBox.warning(self, _("Download failure"), _("Download of the selected area had failed."))
            self.close()
            os.remove(AreaDatabase.path_for(self._area, server_side=False))
        else:
            self._on_map_ready()


    def _update_database(self, area):
        if area > FROZEN_AREA_OSM_ID_OFFSET or not has_api_connectivity():
            self._on_map_ready()
            return
        if not config().general.client_secret:
            secret = create_client(config().general.client_id)
            if not secret:
                raise RuntimeError("Failed to create the server-side client record.")
            config().general.client_secret = secret
            config().save_to_user_config()
        try:
            retriever = SemanticChangeRetriever()
            if retriever.redownload_requested_for(area):
                self._on_redownload_requested(has_progress_dialog=False)
                return
            self._pending_count = retriever.new_change_count_in(area)
        except ConnectionError:
            QMessageBox.warning(self, _("Warning"), _("Could not retrieve changes in the selected area, using the potentially stale local copy."))
            self._on_map_ready()
            return
        if self._pending_count == 0:
            self._on_map_ready()
            return
        generate_changelog = config().changelogs.enabled
        if self._pending_count > 10000 and generate_changelog:
            resp = QMessageBox.question(self, _("Question"), _("The server reports %s pending changes. Do you really want to generate the changelog from all of them? It might take a while.")%self._pending_count)
            if resp == QMessageBox.StandardButton.Yes:
                generate_changelog = False
        self._progress = QProgressDialog(_("Applying changes for the selected database."), None, 0, self._pending_count, self)
        self._progress.setWindowTitle(_("Change application"))
        self._progress.setMinimumDuration(0)
        self._applier = ChangesApplier(area, retriever, generate_changelog)
        self._applier.will_process_change.connect(self._on_will_process_change)
        self._applier.changes_applied.connect(self._on_changes_applied)
        # Force the dialog to be shown
        self._progress.setValue(0)
        self._applier.start()
        
    def _on_redownload_requested(self, has_progress_dialog=True):
        if has_progress_dialog:
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

