import wx
from ..uimanager import get
from shared.model_introspection import get_model_class_display_strings, lookup_model_class_by_display_string
from .search_conditions import SpecifySearchConditionsDialog
from ..geometry_utils import distance_filter

def perform_search(position):
    models = get_model_class_display_strings()
    model_string = wx.GetSingleChoice("Zvolte třídu, nad kterou se má hledání provést", "Třída k prohledání", aChoices=models)
    if model_string:
        conditions_dialog = get().prepare_xrc_dialog(SpecifySearchConditionsDialog, model=lookup_model_class_by_display_string(model_string), alternate_bind_of=["on_fields_tree_sel_changed"])
        if conditions_dialog.ShowModal() != wx.ID_OK:
            return
        query = conditions_dialog.create_query()
        distance = float("inf")
        if conditions_dialog.distance:
            distance = conditions_dialog.distance
        filtered_objects = distance_filter(query, position, distance)
        conditions_dialog.Destroy()
        return filtered_objects
    
    