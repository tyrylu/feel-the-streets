import random
import wx
import os
from sqlalchemy import func
from pygeodesy.ellipsoidalVincenty import LatLon
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController
from .uimanager import get
from .area_selection import AreaSelectionDialog
from .services import map
from shared import Database
from shared.models import Entity

class MainFrame(wx.Frame):
    
    def post_create(self):
        dlg = get().prepare_xrc_dialog(AreaSelectionDialog)
        res = dlg.ShowModal()        
        if res == wx.ID_CANCEL:
            self.Close()
            return
        elif res == wx.ID_OK:
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
    