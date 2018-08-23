import wx
from shared.services import entity_registry
from shared.humanization_utils import get_class_display_name
from shared.models import Entity, IdxEntitiesGeometry
from shared.geometry_utils import xy_ranges_bounding_square
from .search_conditions import SpecifySearchConditionsDialog
from ..geometry_utils import distance_filter
from ..services import map

from uimanager import get

def perform_search(position):
    entities = list(entity_registry().known_entity_classes)
    entity_names = [get_class_display_name(klass) for klass in entities]
    entity = wx.GetSingleChoice(_("Select the class to search"), _("Search class"), aChoices=entity_names)
    if entity:
        conditions_dialog = get().prepare_xrc_dialog(SpecifySearchConditionsDialog, entity=entities[entity_names.index(entity)], alternate_bind_of=["on_fields_tree_sel_changed"])
        if conditions_dialog.ShowModal() != wx.ID_OK:
            conditions_dialog.Destroy()
            return
        conditions = conditions_dialog.create_conditions()
        distance = float("inf")
        if conditions_dialog.distance:
            distance = conditions_dialog.distance
            min_x, min_y, max_x, max_y = xy_ranges_bounding_square(position, distance*2)
            conditions = (Entity.id == IdxEntitiesGeometry.pkid) & (IdxEntitiesGeometry.xmin <= max_x) & (IdxEntitiesGeometry.xmax >= min_x) & (IdxEntitiesGeometry.ymin <= max_y) & (IdxEntitiesGeometry.ymax >= min_y) & conditions
        query = map()._db.query(Entity).filter(conditions)
        filtered_objects = distance_filter(query, position, distance)
        conditions_dialog.Destroy()
        return [filtered.create_osm_entity() for filtered in filtered_objects]
    
    