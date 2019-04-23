import wx
from .server_interaction import has_api_connectivity, get_areas, request_area_creation
from shared import Database
from shared.time_utils import rfc_3339_to_local_string

class AreaSelectionDialog(wx.Dialog):
    xrc_name = "area_selection"

    def post_init(self):
        self.Raise()
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
            area["created_at"] = rfc_3339_to_local_string(area["created_at"])
            area["updated_at"] = rfc_3339_to_local_string(area["updated_at"])
            self._areas.Append(_("{name}: {state}, last updated {updated_at}, created {created_at}").format(**area))
    
    @property
    def selected_map(self):
        return self._area_names[self._areas.Selection]
    
    def on_request_clicked(self, evt):
        name = wx.GetTextFromUser(_("Enter the name of the requested area"), _("Area name requested"))
        if not name:
            return
        reply = request_area_creation(name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            wx.MessageBox(_("The area creation request has been sent successfully. The area will become updated in a few minutes."), _("Success"), style=wx.ICON_INFORMATION)
        else:
            wx.MessageBox(_("The area creation request failed. Response from server: {reply}").format(reply=reply), _("Failure"), style=wx.ICON_ERROR)