import wx
import wx.xrc as xrc
from shapely.geometry.point import Point
from shared.humanization_utils import underscored_to_words
from . import services
from .geometry_utils import closest_point_to, distance_between, bearing_to, to_shapely_point, to_latlon

class ObjectsBrowserDialog(wx.Dialog):
    xrc_name = "objects_browser"

    def post_init(self, title, person, unsorted_objects):
        unsorted_objects = list(unsorted_objects)
        self.Title = title + _(" ({num_objects} objects shown)").format(num_objects=len(unsorted_objects))
        self.EscapeId = xrc.XRCID("close")
        self._person = person
        objects_list = self.FindWindowByName("objects")
        objects = []
        for obj in unsorted_objects:
            objects.append((obj.db_entity.distance_from_current, obj, obj.db_entity.closest_point_to_current))
        objects.sort(key=lambda e: e[0])
        for dist, obj, closest in objects:
            bearing = bearing_to(person.position, closest)
            rel_bearing = (bearing - self._person.direction) % 360
            objects_list.Append(_("{object}: distance {distance:.2} meters, {rel_bearing:.2}° relatively").format(object=obj, distance=dist, rel_bearing=rel_bearing))
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
        for attr in selected.__fields__.values():
            if attr.name == "db_entity":
                continue
            val = getattr(selected, attr.name)
            if not val:
                continue
            props_list.Append("%s: %s"%(underscored_to_words(attr.name), val))
        first = True
        for name, value in selected.additional_fields.items():
            if first:
                props_list.Append(_("Other fields - they can not be searched and are not processed in any way"))
                first = False
            props_list.Append("%s: %s"%(underscored_to_words(name), value))

    @property
    def selected_object(self):
        return self._objects[self.FindWindowByName("objects").Selection]
