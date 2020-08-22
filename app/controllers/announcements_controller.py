from ..services import speech, config
from ..entities import entity_post_enter, entity_post_leave, entity_rotated
from ..controllers.interesting_entities_controller import interesting_entity_in_range
from ..humanization_utils import describe_entity, format_number, describe_relative_angle, TemplateType
from ..geometry_utils import to_shapely_point, closest_point_to, bearing_to, to_latlon

class AnnouncementsController:
    def __init__(self, pov):
        self._point_of_view = pov
        entity_post_enter.connect(self._on_post_enter)
        entity_post_leave.connect(self._on_post_leave)
        entity_rotated.connect(self._on_rotated)
        interesting_entity_in_range.connect(self._interesting_entity_in_range)
    
    def _on_post_enter(self, sender, enters):
        if sender is self._point_of_view:
            speech().speak(_("You are entering {enters}.").format(enters=describe_entity(enters)))
            
    def _on_post_leave(self, sender, leaves):
        if sender is self._point_of_view:
            speech().speak(_("You are leaving {leaves}").format(leaves=describe_entity(leaves)))

    def _on_rotated(self, sender):
        if self._point_of_view is sender:
            speech().speak(_("{degrees} degrees").format(degrees=format_number(sender.direction, config().presentation.angle_decimal_places)))

    def _interesting_entity_in_range(self, sender, entity):
        shapely_point = to_shapely_point(self._point_of_view.position)
        closest_point = to_latlon(closest_point_to(shapely_point, entity.geometry))
        bearing = bearing_to(self._point_of_view.position, closest_point)
        rel_bearing = (bearing - self._point_of_view.direction) % 360
        speech().speak(_("{angle_description} is a {entity_description}").format(angle_description=describe_relative_angle(rel_bearing), entity_description=describe_entity(entity, template_type=TemplateType.short)))
