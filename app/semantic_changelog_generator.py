import json
import osm_db
from osm_db import ChangeType as CT
from .humanization_utils import underscored_to_words, format_field_value, get_field_type, describe_entity
from .services import map

def get_dictchange_description(dictchange, entity_fields):
    field_type = get_field_type(dictchange.key, entity_fields)
    if dictchange.kind == CT.Create:
        return _("{property}: addition with value {value}").format(property=underscored_to_words(dictchange.key), value=format_field_value(dictchange.new_value, field_type))
    elif dictchange.kind == CT.Update:
        return _("{property}: change from {old} to {new}").format(property=underscored_to_words(dictchange.key), old=format_field_value(dictchange.old_value, field_type), new=format_field_value(dictchange.new_value, field_type))
    elif dictchange.kind == CT.Remove:
        return _("{property}: removal").format(property=underscored_to_words(dictchange.key))
    else:
        raise RuntimeError("Unknown dictchange kind %s."%dictchange.kind)

def get_change_description(change, entity, include_geometry_changes=False):
    fields = osm_db.EntityMetadata.for_discriminator(entity.discriminator).fields
    if change.type == CT.Remove:
        return "* " + _("Object {osm_id} ({object}) was deleted").format(osm_id=change.osm_id, object=describe_entity(entity)) + "\n"
    elif change.type == CT.Create:
        msg = "* " + _("New object created") + "\n"
        for propchange in change.property_changes:
            if propchange.key == "data":
                data = json.loads(propchange.new_value)
                for key, val in data.items():
                    field_type = get_field_type(key, fields)
                    msg += "{0}: {1}\n".format(underscored_to_words(key), format_field_value(val, field_type))
            else:
                if propchange.key == "geometry" and not include_geometry_changes:
                    continue
                msg += "{0}: {1}\n".format(underscored_to_words(propchange.key), propchange.new_value)
        return msg
    elif change.type == CT.Update:
        msg = "* " + _("Object {osm_id} ({object}) was changed").format(osm_id=change.osm_id, object=describe_entity(entity)) + "\n"
        for subchange in change.property_changes:
            if subchange.key == "geometry" and not include_geometry_changes:
                msg += _("Geometry was changed.") + "\n"
            else:
                msg += get_dictchange_description(subchange, fields) + "\n"
        for subchange in change.data_changes:
            msg += get_dictchange_description(subchange, fields) + "\n"
        return msg
    else:
        breakpoint()
        raise RuntimeError("Invalid semantic change type %s."%change.type)