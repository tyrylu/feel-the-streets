import wx
from .humanization_utils import underscored_to_words

class AreasBrowser(wx.Dialog):
    xrc_name = "areas_browser"

    def post_init(self, areas):
        self._areas = list(areas.items())
        areas_list = self.FindWindowByName("areas_list")
        for id, data in self._areas:
            areas_list.Append(_("Area {id}").format(id=id))
        areas_list.Selection = 0
        self.on_areas_list_listbox(None)

    def on_areas_list_listbox(self, evt):
        index = self.FindWindowByName("areas_list").Selection
        props = self.FindWindowByName("props")
        props.Clear()
        for key, value in self._areas[index][1].items():
            props.Append(f"{underscored_to_words(key)}: {value}")

    @property
    def selected_area_id(self):
        return self._areas[self.FindWindowByName("areas_list").Selection][0]