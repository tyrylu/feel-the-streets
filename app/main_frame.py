import random
import wx
import os
import datetime
from sqlalchemy import func
from pygeodesy.ellipsoidalVincenty import LatLon
import humanfriendly
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController
from .uimanager import get
from .area_selection import AreaSelectionDialog
from .services import map
from .server_interaction import download_area_database, SemanticChangeRetriever
from .semantic_changelog_generator import get_change_description
from shared import Database
from shared.models import Entity

class MainFrame(wx.Frame):

    def post_create(self):
        self._download_progress_dialog = None
        dlg = get().prepare_xrc_dialog(AreaSelectionDialog)
        res = dlg.ShowModal()        
        if res == wx.ID_CANCEL:
            self.Close()
            return
        elif res == wx.ID_OK:
            if not os.path.exists(Database.get_database_file(dlg.selected_map, server_side=False)):
                self._download_database(dlg.selected_map)
            else:
                self._update_database(dlg.selected_map)
            self.SetFocus()
            map.set_call_args(dlg.selected_map, server_side=False)
        self._app_controller = ApplicationController(self)
        entity = map()._db.query(Entity).filter(func.json_extract(Entity.data, "$.osm_id").startswith("n")).first()
        lon = map()._db.scalar(entity.geometry.x)
        lat = map()._db.scalar(entity.geometry.y)
        person = Person(map(), LatLon(lat, lon))
        self._person_controller = InteractivePersonController(person)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        person.move_to_current()
    
    def _download_progress_callback(self, total, so_far):
        if not self._download_progress_dialog:
            self._download_progress_dialog = wx.ProgressDialog(_("Download in progress"), _("Downloading the selected database."), parent=self, style=wx.PD_APP_MODAL|wx.PD_ESTIMATED_TIME|wx.PD_ELAPSED_TIME|wx.PD_AUTO_HIDE, maximum=total)
        self._download_progress_dialog.Update(so_far, _("Downloading the selected database. Downloaded {so_far} of {total}.").format(so_far=humanfriendly.format_size(so_far), total=humanfriendly.format_size(total)))


    def _download_database(self, area):
        res = download_area_database(area, self._download_progress_callback)
        if not res:
            wx.MessageBox(_("Download of the selected area had failed."), _("Download failure"), style=wx.ICON_ERROR)
            self.Close()
            return


    def _update_database(self, area):
        retriever = SemanticChangeRetriever()
        pending_count = retriever.new_change_count_in(area)
        if not pending_count:
            return
        db = Database(area, server_side=False)
        progress = wx.ProgressDialog(_("Change application"), _("Applying changes for the selected database."), style=wx.PD_APP_MODAL|wx.PD_ESTIMATED_TIME|wx.PD_ELAPSED_TIME|wx.PD_AUTO_HIDE, maximum=pending_count)
        changelog_path = os.path.join(Database.get_database_storage_root(server_side=False), "..", "changelogs", "{0}_{1}.txt".format(area, datetime.datetime.now().isoformat().replace(":", "_")))
        os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
        changelog = open(changelog_path, "w", encoding="UTF-8")
        for nth, change in enumerate(retriever.new_changes_in(area)):
            progress.Update(nth, _("Applying changes for the selected database, change {nth} of {total}").format(nth=nth, total=pending_count))
            db.apply_change(change)
            changelog.write(get_change_description(change))
        db.commit()
        changelog.close()
        changelog_size = os.path.getsize(changelog_path)
        resp = wx.MessageBox(_("Successfully applied {total} changes. A changelog of size {size} was generated, do you want to view it now?").format(total=pending_count, size=changelog_size), _("Success"), style=wx.ICON_QUESTION|wx.YES_NO)
