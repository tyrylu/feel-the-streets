import random
import wx
import glob
from geodesy.ellipsoidalVincenty import LatLon
from .entities import Person
from .controllers import InteractivePersonController, ApplicationController, SoundController, AnnouncementsController
from .uimanager import get
from .services import map
from shared.models import Entity
from shared.models.enums import OSMObjectType

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__()
        maps = glob.glob("*.db")
        user_maps = [map.split(".")[0] for map in maps]
        map_name = wx.GetSingleChoice("Zvolte mapu", "Výběr mapy", aChoices=user_maps)
        if map_name:
            map.set_call_args(map_name)
            self._map = map()
        
    def post_create(self):
        entity = self._map._db.query(Entity).filter(Entity.osm_type == OSMObjectType.node)[0]
        lon = self._map._db.scalar(entity.geometry.x)
        lat = self._map._db.scalar(entity.geometry.y)
        person = Person(self._map, LatLon(lat, lon))
        self._person_controller = InteractivePersonController(person)
        self._app_controller = ApplicationController(self)
        self._sound_controller = SoundController(person)
        self._announcements_controller = AnnouncementsController(person)
        person.move_to_current()
    