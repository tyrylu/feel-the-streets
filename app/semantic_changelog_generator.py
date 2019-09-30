import json
from shared.humanization_utils import underscored_to_words
import osm_db
from .services import map

known_enums = osm_db.Enum.all_known()

def get_field_type(key, fields):
    if key in fields:
        return fields[key].type_name
    else:
        return "str"
    

def format_value(field_value, field_type):
    if field_type in known_enums:
        try:
            field_value = underscored_to_words(osm_db.Enum.with_name(field_type).name_for_value(field_value))
        except ValueError: pass
    return field_value

def get_dictchange_description(dictchange, entity_fields):
    field_type = get_field_type(dictchange.key, entity_fields)
    if dictchange.kind is osm_db.CHANGE_CREATE:
        return _("{property}: addition with value {value}").format(property=underscored_to_words(dictchange.key), value=format_value(dictchange.new_value, field_type))
    elif dictchange.kind is osm_db.CHANGE_UPDATE:
        return _("{property}: change from {old} to {new}").format(property=underscored_to_words(dictchange.key), old=format_value(dictchange.old_value, field_type), new=format_value(dictchange.new_value, field_type))
    elif dictchange.kind is osm_db.CHANGE_REMOVE:
        return _("{property}: removal").format(property=underscored_to_words(dictchange.key))
    else:
        raise RuntimeError("Unknown dictchange kind %s."%dictchange.kind)

def get_change_description(change, entity, include_geometry_changes=False):
    fields = osm_db.EntityMetadata.for_discriminator(entity.discriminator).fields
    if change.type is osm_db.CHANGE_REMOVE:
        return "* " + _("Object {osm_id} ({object}) was deleted").format(osm_id=change.osm_id, object=entity) + "\n"
    elif change.type is osm_db.CHANGE_CREATE:
        msg = "* " + _("New object created") + "\n"
        for propchange in change.property_changes:
            if propchange.key == "data":
                data = json.loads(propchange.new_value)
                for key, val in data.items():
                    field_type = get_field_type(key, fields)
                    msg += "{0}: {1}\n".format(underscored_to_words(key), format_value(val, field_type))
            else:
                if propchange.key == "geometry" and not include_geometry_changes:
                    continue
                msg += "{0}: {1}\n".format(underscored_to_words(propchange.key), propchange.new_value)
        return msg
    elif change.type is osm_db.CHANGE_UPDATE:
        msg = "* " + _("Object {osm_id} ({object}) was changed").format(osm_id=change.osm_id, object=entity) + "\n"
        for subchange in change.property_changes:
            if subchange.key == "geometry" and not include_geometry_changes:
                msg += _("Geometry was changed.") + "\n"
            else:
                msg += get_dictchange_description(subchange, fields) + "\n"
        for subchange in change.data_changes:
            msg += get_dictchange_description(subchange, fields) + "\n"
        return msg
    else:
        raise RuntimeError("Invalid semantic change type %s."%change.type)