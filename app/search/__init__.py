import wx
from shared.services import entity_registry
from shared.humanization_utils import get_class_display_name
from ..uimanager import get
from .search_conditions import SpecifySearchConditionsDialog
from ..geometry_utils import distance_filter


def perform_search(position):
    entities = list(entity_registry().known_entity_classes)
    entity_names = [get_class_display_name(klass) for klass in entities]
    entity = wx.GetSingleChoice("Zvolte třídu, nad kterou se má hledání provést", "Třída k prohledání", aChoices=entity_names)
    if entity:
        conditions_dialog = get().prepare_xrc_dialog(SpecifySearchConditionsDialog, entity=entities[entity_names.index(entity)], alternate_bind_of=["on_fields_tree_sel_changed"])
        if conditions_dialog.ShowModal() != wx.ID_OK:
            conditions_dialog.Destroy()
            return
        query = conditions_dialog.create_query()
        distance = float("inf")
        if conditions_dialog.distance:
            distance = conditions_dialog.distance
        filtered_objects = distance_filter(query, position, distance)
        conditions_dialog.Destroy()
        return [filtered.create_osm_entity() for filtered in filtered_objects]
    
    