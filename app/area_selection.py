import wx
from .server_interaction import has_api_connectivity, get_areas
from shared import Database
from shared.time_utils import utc_timestamp_to_local_string

class AreaSelectionDialog(wx.Dialog):
    xrc_name = "area_selection"

    def post_init(self):
        self._areas = self.FindWindowByName("areas")
        if has_api_connectivity():
            available = get_areas()
        else:
            available = Database.get_local_databases_info(server_side=False)
            self.FindWindowByName("request").Disable()
        self._area_names = [a["name"] for a in available]
        self._fill_areas(available)

    def _fill_areas(self, areas):
        for area in areas:
            area["created_at"] = utc_timestamp_to_local_string(area["created_at"])
            area["updated_at"] = utc_timestamp_to_local_string(area["updated_at"])
            self._areas.Append(_("{name}: created at: {created_at}, last updated: {updated_at}, state: {state}").format(**area))
    @property
    def selected_map(self):
        return self._area_names[self._areas.Selection]