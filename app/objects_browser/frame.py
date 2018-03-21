import enum
import inspect
import wx
import wx.xrc as xrc
from shapely.geometry.point import Point
from shared.humanization_utils import underscored_to_words
from .. import services
from ..geometry_utils import closest_point_to, distance_between, bearing_to, to_shapely_point, to_latlon
from . import object_actions
from .object_actions.action import ObjectAction
from shared.entities import OSMEntity

def action_execution_handler_factory(action, entity):
    def handler(evt):
        return action.execute(entity)
    return handler

class ObjectsBrowserFrame(wx.Frame):
    xrc_name = "objects_browser"

    def post_init(self, title, person, unsorted_objects):
        unsorted_objects = list(unsorted_objects)
        self.Title = title + _(" ({num_objects} objects shown)").format(num_objects=len(unsorted_objects))
        self._person = person
        objects_list = self.FindWindowByName("objects")
        objects = []
        for obj in unsorted_objects:
            objects.append((obj.db_entity.distance_from_current, obj, obj.db_entity.closest_point_to_current))
        objects.sort(key=lambda e: e[0])
        for dist, obj, closest in objects:
            bearing = bearing_to(person.position, closest)
            rel_bearing = (bearing - self._person.direction) % 360
            objects_list.Append(_("{object}: distance {distance:.2f} meters, {rel_bearing:.2f}° relatively").format(object=obj, distance=dist, rel_bearing=rel_bearing))
        self._objects = objects
        self.Bind(wx.EVT_CHAR_HOOK, self._close_using_esc)
        self._all_actions = []
        for member in object_actions.__dict__.values():
            if inspect.isclass(member) and issubclass(member, ObjectAction):
                self._all_actions.append(member)
        objects_list.Selection = 0
        self._root_item = self.FindWindowByName("props").AddRoot("Never to be seen")
        self.on_objects_listbox(None)


    def on_close_clicked(self, evt):
        self.Close()
    
    def on_goto_clicked(self, evt):
        self._person.move_to(self.selected_object[2])
        self.Close()
    
    def on_objects_listbox(self, evt):
        sel = self.FindWindowByName("objects").Selection
        selected = self._objects[sel][1]
        props_list = self.FindWindowByName("props")
        props_list.DeleteChildren(self._root_item)
        fields_by_group = {"common": [], "specific": [], "additional": []}
        common_fields = set(OSMEntity.__fields__.keys())
        for attr in selected.__fields__.values():
            if attr.name == "db_entity":
                continue
            val = getattr(selected, attr.name)
            if not val:
                continue
            if isinstance(val, enum.Enum):
                val = underscored_to_words(val.name)
            value_str = "%s: %s"%(underscored_to_words(attr.name), val)
            if attr.name in common_fields:
                fields_by_group["common"].append(value_str)
            else:
                fields_by_group["specific"].append(value_str)
        for name, value in selected.additional_fields.items():
            fields_by_group["additional"].append("%s: %s"%(underscored_to_words(name), value))
        root = self._root_item
        common = props_list.AppendItem(root, _("Common properties"))
        for val in fields_by_group["common"]:
            props_list.AppendItem(common, val)
        specific = None
        if fields_by_group["specific"]:
            specific = props_list.AppendItem(root, _("Specific properties"))
            for val in fields_by_group["specific"]:
                props_list.AppendItem(specific, val)
        if fields_by_group["additional"]:
            other = props_list.AppendItem(root, _("Other fields - they can not be searched and are not processed in any way"))
            for val in fields_by_group["additional"]:
                props_list.AppendItem(other, val)
        if specific:
            props_list.Expand(specific)
            props_list.SelectItem(specific)
        menu = self.MenuBar.Menus[0][0]
        for item in menu.MenuItems:
            menu.Delete(item)
        for action in self._all_actions:
            if action.executable(selected):
                mi = menu.Append(wx.ID_ANY, action.label)
                self.Bind(wx.EVT_MENU, action_execution_handler_factory(action, selected), mi)

    @property
    def selected_object(self):
        return self._objects[self.FindWindowByName("objects").Selection]

    def _close_using_esc(self, evt):
        if evt.KeyCode == wx.WXK_ESCAPE:
            self.Close()
        else:
            evt.Skip()

    def on_copypropvalue_selected(self, evt):
        prop_list = self.FindWindowByName("props")
        prop = prop_list.GetItemText(prop_list.Selection)
        val = prop.split(": ", 1)[1]
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(val))
            wx.TheClipboard.Close()
    
    def on_copypropname_selected(self, evt):
        prop_list = self.FindWindowByName("props")
        prop = prop_list.GetItemText(prop_list.Selection)
        name = prop.split(": ", 1)[0]
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(name))
            wx.TheClipboard.Close()

    def on_copypropline_selected(self, evt):
        prop_list = self.FindWindowByName("props")
        prop = prop_list.GetItemText(prop_list.Selection)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(prop))
            wx.TheClipboard.Close()