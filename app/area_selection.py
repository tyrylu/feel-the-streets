import glob
import logging
import os
import wx
import pendulum
from .server_interaction import has_api_connectivity, get_areas, request_area_creation, get_areas_with_name
from uimanager import get
from .time_utils import rfc_3339_to_local_string
from .areas_browser import AreasBrowser
from osm_db import AreaDatabase

log = logging.getLogger(__name__)


def get_local_area_infos():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for("someplace", False))
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        name = os.path.basename(db_file).replace(".db", "")
        mtime = pendulum.from_timestamp(os.path.getmtime(db_file)).to_rfc3339_string()
        ctime = pendulum.from_timestamp(os.path.getctime(db_file)).to_rfc3339_string()
        # Cache names for offline use, they're ugly now.
        results.append({"osm_id": name, "name":name, "updated_at": mtime, "state": "local", "created_at": ctime})
    return results


class AreaSelectionDialog(wx.Dialog):
    xrc_name = "area_selection"

    def post_init(self):
        self.Raise()
        self._areas = self.FindWindowByName("areas")
        if has_api_connectivity():
            available = get_areas()
        else:
            available = get_local_area_infos()
            self.FindWindowByName("request").Disable()
        self._area_ids = [a["osm_id"] for a in available]
        self._fill_areas(available)

    def _fill_areas(self, areas):
        for area in areas:
            area["created_at"] = rfc_3339_to_local_string(area["created_at"])
            area["updated_at"] = rfc_3339_to_local_string(area["updated_at"])
            self._areas.Append(_("{name}: {state}, last updated {updated_at}, created {created_at}").format(**area))
    
    @property
    def selected_map(self):
        return self._area_ids[self._areas.Selection]
    
    def on_request_clicked(self, evt):
        name = wx.GetTextFromUser(_("Enter the name of the requested area"), _("Area name requested"))
        if not name:
            return
        candidates = get_areas_with_name(name)
        if not candidates:
            wx.MessageBox(_("The area with name {name} does not correspond to any OSM areas.").format(name=name), _("Area not found"), style=wx.ICON_ERROR)
            return
        if len(candidates) == 1:
            area_id = next(iter(candidates.keys()))
            log.info("Only one candidate with an admin level of %s and id %s.", next(iter(candidates.values()))["admin_level"], area_id)
        else:
            dialog = get().prepare_xrc_dialog(AreasBrowser, areas=candidates)
            res = dialog.ShowModal()
            dialog.Destroy()
            if res == wx.ID_OK:
                area_id = dialog.selected_area_id
            else:
                return
        reply = request_area_creation(area_id, name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            wx.MessageBox(_("The area creation request has been sent successfully. The area will become updated in a few minutes."), _("Success"), style=wx.ICON_INFORMATION)
        
        elif reply and isinstance(reply, dict) and "state" in reply and reply["state"] in {"Creating", "Updated", "ApplyingChanges", "GettingChanges"}:
            wx.MessageBox(_("The area creation request has already been sent."), _("Success"), style=wx.ICON_INFORMATION)
        else:
            wx.MessageBox(_("The area creation request failed. Response from server: {reply}").format(reply=reply), _("Failure"), style=wx.ICON_ERROR)