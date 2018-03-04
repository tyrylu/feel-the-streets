import random
import wx
import os
from sqlalchemy import func
from pygeodesy.ellipsoidalVincenty import LatLon
import humanfriendly
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController
from .uimanager import get
from .area_selection import AreaSelectionDialog
from .services import map
from .server_interaction import download_area_database
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
                res = download_area_database(dlg.selected_map, self._download_progress_callback)
                if not res:
                    wx.MessageBox(_("Download of the selected area had failed."), _("Download failure"), style=wx.ICON_ERROR)
                    self.Close()
                    return
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
