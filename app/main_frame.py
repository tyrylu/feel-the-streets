import random
import wx
import glob
import os
from sqlalchemy import func
from pygeodesy.ellipsoidalVincenty import LatLon
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController
from .uimanager import get
from .services import map
from shared import Database
from shared.models import Entity
from shared.entities.enums import OSMObjectType

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__()
        maps = glob.glob("%s/*.db"%Database.get_database_storage_root())
        user_maps = [os.path.basename(map).split(".")[0] for map in maps]
        map_name = wx.GetSingleChoice(_("Select the map"), _("Map selection"), aChoices=user_maps)
        if map_name:
            map.set_call_args(map_name)
            self._map = map()
        
    def post_create(self):
        self._app_controller = ApplicationController(self)
        entity = self._map._db.query(Entity).filter(func.json_extract(Entity.data, "$.osm_id").startswith("n")).first()
        lon = self._map._db.scalar(entity.geometry.x)
        lat = self._map._db.scalar(entity.geometry.y)
        person = Person(self._map, LatLon(lat, lon))
        self._person_controller = InteractivePersonController(person)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        person.move_to_current()
    