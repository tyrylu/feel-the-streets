from PySide6.QtWidgets import QInputDialog, QProgressDialog
from osm_db import EntityMetadata, all_known_discriminators, EntitiesQuery, FieldNamed
from ..humanization_utils import get_class_display_name
from .search_conditions import SpecifySearchConditionsDialog
from .query_executor import QueryExecutor
from ..geometry_utils import xy_ranges_bounding_square

def create_query(discriminator, current_position, distance, conditions):
    query = EntitiesQuery()
    if distance < float("inf"):
        min_x, min_y, max_x, max_y = xy_ranges_bounding_square(current_position, distance*2)
        query.set_rectangle_of_interest(min_x, max_x, min_y, max_y)
    # We have no easy way how to determine the children of a class, so we would have to iterate through all the classes anyway.
    # There's an assumption that the excluded classes will not be as numerous (for example almost anything is named), so find the exceptions instead.
    excluded_discriminators = set()
    for candidate in all_known_discriminators():
        found = False
        metadata = EntityMetadata.for_discriminator(candidate)
        while metadata:
            if metadata.discriminator == discriminator:
                found = True
                break
            metadata = metadata.parent_metadata
        if not found:
            excluded_discriminators.add(candidate)
    query.set_excluded_discriminators(list(excluded_discriminators))
    for condition in conditions:
        query.add_condition(condition)
    return query

def create_query_for_name_search(name):
    return create_query("Named", None, float("inf"), [FieldNamed("name").like("%{}%".format(name))])

def create_query_for_address_search(address):
    # Try to be nice to the user and ignore whitespace differences
    address = address.strip()
    street, number = address.rsplit(" ", 1)
    street = street.strip()
    housenumber_condition = FieldNamed("address.housenumber").eq(number)
    if "/" not in number: # It might be a part of a number composed of more parts
        housenumber_condition = housenumber_condition.or_(FieldNamed("address.housenumber").like(f"{number}/%")).or_(FieldNamed("address.housenumber").like(f"%/{number}"))
    return create_query("Addressable", None, float("inf"), [FieldNamed("address.street").eq(street), housenumber_condition])

def get_query_from_user(parent, position):
    entities = all_known_discriminators()
    name_mapping = {}
    for entity in entities:
        name_mapping[get_class_display_name(entity)] = entity
    entity, ok = QInputDialog.getItem(parent, _("Search class"), _("Select the class to search"), sorted(name_mapping.keys()), editable=False)
    if not ok:
        return
    discriminator = name_mapping[entity]
    conditions_dialog = SpecifySearchConditionsDialog(parent, entity=discriminator)
    if conditions_dialog.exec_() != SpecifySearchConditionsDialog.Accepted:
        return
    distance = conditions_dialog.distance or float("inf")
    query = create_query(discriminator, position, distance, conditions_dialog.create_conditions())
    return query, distance
    