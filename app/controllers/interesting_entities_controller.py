from blinker import Signal
from ..entities import entity_post_move
from ..services import config, map
from ..geometry_utils import distance_filter

interesting_entity_in_range = Signal()
interesting_entity_out_of_range = Signal()
request_interesting_entities = Signal()

def entity_has_none_of_these_fields(entity, *field_names):
    for field_name in field_names:
        if entity.value_of_field(field_name) is not None:
            return False
    return True

def is_interesting(entity):
    # For our purposes, the following discriminators are not interesting.
    not_interesting_discriminators = {"Crossing", "Addressable", "Barrier", "PowerLine", "NoExit", "Entrance", "RailWay", "Tree", "Steps"}
    if entity.discriminator in not_interesting_discriminators:
        return False
    # Filter out uninteresting buildings
    if entity.discriminator == "Building" and entity_has_none_of_these_fields(entity, "amenity", "education", "artwork_type", "garden_type", "seamark_type", "diplomatic", "landuse", "historic_type", "industrial_type", "man_made", "leisure_type", "emergency"):
        return False
    return True

def  filter_interesting_entities(objects):
    res = set()
    for object in objects:
        if is_interesting(object):
            res.add(object)
    return res

class InterestingEntitiesController:
    def __init__(self, point_of_view):
        self._point_of_view = point_of_view
        self._interesting_entities = set()
        entity_post_move.connect(self._entity_post_move)
        request_interesting_entities.connect(self._interesting_entities_requested)

    def _entity_post_move(self, sender):
        if sender is not self._point_of_view: return
        rough_distant = map().roughly_within_distance(sender.position, config().presentation.near_by_radius)
        interesting = filter_interesting_entities(rough_distant)
        within_distance = set(distance_filter(interesting, self._point_of_view.position, config().presentation.near_by_radius))
        in_range = within_distance.difference(self._interesting_entities)
        out_of_range = self._interesting_entities.difference(within_distance)
        for entity in in_range:
            interesting_entity_in_range.send(self, entity=entity)
        for entity in out_of_range:
            interesting_entity_out_of_range.send(self, entity=entity)
        self._interesting_entities = within_distance

    def _interesting_entities_requested(self, sender):
        return self._interesting_entities