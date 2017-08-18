import wx
from .geometry_utils import closest_point_to, distance_between, bearing_to, to_shapely_point, to_latlon

from shapely.geometry.point import Point
import wx.xrc as xrc
from sqlalchemy import inspect
from . import services

class ObjectsBrowserDialog(wx.Dialog):
    xrc_name = "objects_browser"
    def post_init(self, title, person, unsorted_objects):
        self.Title = title
        self.EscapeId = xrc.XRCID("close")
        self._person = person
        objects_list = self.FindWindowByName("objects")
        cur_point = to_shapely_point(person.position)
        objects = []
        for obj in unsorted_objects:
            closest = closest_point_to(cur_point, obj.geometry)
            closest_latlon = to_latlon(closest)
            dist = distance_between(person.position, closest_latlon)
            objects.append((dist, obj, closest_latlon))
        objects.sort(key=lambda e: e[0])
        for dist, obj, closest in objects:
            bearing = bearing_to(person.position, closest)
            rel_bearing = (bearing - self._person.direction) % 360
            objects_list.Append("%s: vzdálenost %.2f metrů, %.2f° relativně"%(obj, dist, rel_bearing))
        self._objects = objects
        objects_list.Selection = 0
        self.on_objects_listbox(None)
    def on_close_clicked(self, evt):
        self.EndModal(0)
    def on_goto_clicked(self, evt):
        self.EndModal(1)
    def on_objects_listbox(self, evt):
        sel = self.FindWindowByName("objects").Selection
        selected = self._objects[sel][1]
        props_list = self.FindWindowByName("props")
        props_list.Clear()
        
        for name, attr in inspect(selected).attrs.items():
            val = attr.value
            if not val:
                continue
            if name == "geometry" or name == "original_geometry":
                val = services.map().geometry_to_wkt(val)
            props_list.Append("%s: %s"%(name, val))
    @property
    def selected_object(self):
        return self._objects[self.FindWindowByName("objects").Selection]
