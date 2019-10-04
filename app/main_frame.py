import logging
import wx
import os
import json
import datetime
import webbrowser
from pygeodesy.ellipsoidalVincenty import LatLon
import bitmath
import shapely.wkb as wkb
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController, LastLocationController
from .area_selection import AreaSelectionDialog
from .services import map
from .server_interaction import download_area_database, SemanticChangeRetriever, has_api_connectivity
from .semantic_changelog_generator import get_change_description
from osm_db import AreaDatabase, EntitiesQuery, CHANGE_REMOVE
from uimanager import get

log = logging.getLogger(__name__)

def format_size(num_bytes):
    size = bitmath.Byte(num_bytes)
    return size.best_prefix().format("{value:.2f} {unit}")

class MainFrame(wx.Frame):

    def post_create(self):
        self._download_progress_dialog = None
        dlg = get().prepare_xrc_dialog(AreaSelectionDialog)
        res = dlg.ShowModal()        
        if res == wx.ID_CANCEL:
            self.Close()
            return
        elif res == wx.ID_OK:
            if not os.path.exists(AreaDatabase.path_for(dlg.selected_map, server_side=False)):
                self._download_database(dlg.selected_map)
            else:
                self._update_database(dlg.selected_map)
            self.SetFocus()
            map.set_call_args(dlg.selected_map)
        self._app_controller = ApplicationController(self)
        person = Person(map(), LatLon(0, 0))
        self._person_controller = InteractivePersonController(person)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        self._last_location_controller = LastLocationController(person)
        if not self._last_location_controller.restored_position:
            query = EntitiesQuery()
            query.set_limit(1)
            entity = map()._db.get_entities(query)[0]
            geom = wkb.loads(entity.geometry)
            lon = geom.x
            lat = geom.y
            person.move_to(LatLon(lat, lon))

   
    def _download_progress_callback(self, total, so_far):
        if not self._download_progress_dialog:
            self._download_progress_dialog = wx.ProgressDialog(_("Download in progress"), _("Downloading the selected database."), parent=self, style=wx.PD_APP_MODAL|wx.PD_ESTIMATED_TIME|wx.PD_ELAPSED_TIME|wx.PD_AUTO_HIDE)
        percentage = int((so_far/total)*100)
        self._download_progress_dialog.Update(percentage, _("Downloading the selected database. Downloaded {so_far} of {total}.").format(so_far=format_size(so_far), total=format_size(total)))

    def _download_database(self, area):
        res = download_area_database(area, self._download_progress_callback)
        if not res:
            wx.MessageBox(_("Download of the selected area had failed."), _("Download failure"), style=wx.ICON_ERROR)
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
        db.begin()
        progress = wx.ProgressDialog(_("Change application"), _("Applying changes for the selected database."), style=wx.PD_APP_MODAL|wx.PD_ESTIMATED_TIME|wx.PD_ELAPSED_TIME|wx.PD_AUTO_HIDE, maximum=pending_count)
        changelog_path = os.path.join(os.path.dirname(AreaDatabase.path_for("someplace", server_side=False)), "..", "changelogs", "{0}_{1}.txt".format(area, datetime.datetime.now().isoformat().replace(":", "_")))
        os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
        changelog = open(changelog_path, "w", encoding="UTF-8")
        for nth, change in enumerate(retriever.new_changes_in(area)):
            progress.Update(nth, _("Applying changes for the selected database, change {nth} of {total}").format(nth=nth, total=pending_count))
            entity = None
            if change.type is CHANGE_REMOVE:
                entity = db.get_entity(change.osm_id)
            db.apply_change(change)
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
        resp = wx.MessageBox(_("Successfully applied {total} changes. A changelog of size {size} was generated, do you want to view it now?").format(total=pending_count, size=format_size(changelog_size)), _("Success"), style=wx.ICON_QUESTION|wx.YES_NO)
        if resp == wx.YES:
            # Somewhat hacky, but os.startfile is not cross platform and the webbrowser way appears to be.
            webbrowser.open(changelog_path)

