from collections import defaultdict
import enum
import re
import builtins
from osm_db import EntityMetadata, Enum
import jinja2
import logging
from PySide2.QtCore import QLocale
from .services import config


class TemplateType(enum.Enum):
    long = 1
    short = 2

known_enums = Enum.all_known()
jinja2_env = jinja2.Environment(loader=jinja2.BaseLoader())
template_cache = defaultdict(dict)
locale = QLocale()


log = logging.getLogger(__name__)

def get_template_string(metadata, template_type):
    return metadata.short_display_template if template_type is TemplateType.short else metadata.long_display_template # If we add a third type, we'll have to change this oneliner to something with more lines.

def get_template(metadata, template_type):
    if template_type not in template_cache[metadata.discriminator]:
        template = get_template_string(metadata, template_type)
        template_cache[metadata.discriminator][template_type] = jinja2_env.from_string(template)
    return template_cache[metadata.discriminator][template_type]

def underscored_to_words(underscored):
    _ = getattr(builtins, "_", lambda s: s)
    if not underscored:
        underscored = "unknown"
    underscored = underscored.replace("_", " ")
    underscored = re.sub(r"^\w", lambda m: m.group(0).upper(), underscored)
    return _(underscored)

def get_field_type(key, fields):
    if key in fields:
        return fields[key].type_name
    else:
        return "str"
    

def format_field_value(field_value, field_type, template_type=TemplateType.long):
    if field_type in known_enums:
        try:
            if isinstance(field_value, str):
                log.warn("Field value %s of the enum %s expected to be an int.", field_value, field_type)
                return underscored_to_words(field_value)
            return underscored_to_words(Enum.with_name(field_type).name_for_value(field_value)) or field_value
        except ValueError: pass
    try:
        metadata = EntityMetadata.for_discriminator(field_type)
    except KeyError:
        return field_value
    return describe_nested_object(field_value, metadata, template_type)
    
def format_class_name(name):
    return re.sub(r"([a-z\d])([A-Z])([a-z\d])", lambda m: "%s %s%s"%(m.group(1), m.group(2).lower(), m.group(3)), name)

def get_class_display_name(klass):
    _ = getattr(builtins, "_", lambda s: s)
    return _(format_class_name(klass))

def describe_entity(entity, metadata=None, template_type=TemplateType.long):
    if not metadata:
        metadata = EntityMetadata.for_discriminator(entity.discriminator)
    template_source = metadata
    while True:
        if get_template_string(template_source, template_type):
            break
        template_source = template_source.parent_metadata
    context = {}
    fields = metadata.all_fields
    for field_name in entity.defined_field_names():
        if field_name not in fields:
            continue
        value = entity.value_of_field(field_name)
        context[field_name] = format_field_value(value, fields[field_name].type_name)
    # Special variables
    if template_source.parent_metadata:
        context["parent_display"] = describe_entity(entity, template_source.parent_metadata)
    context["class_name_display"] = get_class_display_name(entity.discriminator)
    template_object = get_template(template_source, template_type)
    return template_object.render(**context)

def describe_nested_object(obj, metadata, template_type):
    context = {}
    for key, val in obj.items():
        context[key] = format_field_value(val, metadata.fields[key].type_name)
    return get_template(metadata, template_type).render(**context)

def format_number(value, decimal_places):
    rounded = round(value, decimal_places)
    # Make it an integer if the precision allows
    if int(rounded) == rounded:
        rounded = int(rounded)
    rounded_str = str(rounded)
    rounded_str = rounded_str.replace(".", locale.decimalPoint())
    return rounded_str

def describe_relative_angle(angle):
    if 5 <= angle < 85:
        return _("On the front right")
    elif 85 <= angle < 95:
        return _("On the right")
    elif 95 <= angle < 175:
        return _("On the rear right")
    elif 175 <= angle < 185:
        return _("Behind")
    elif 185 <= angle < 265:
        return _("On the rear left")
    elif 265 <= angle < 275:
        return _("On the left")
    elif 275 <= angle < 355:
        return _("On the front left")
    elif (355 <= angle <= 360) or (0 <= angle < 5):
        return _("In the front")
    else:
        raise ValueError("Unhandled relative angle {}".format(angle))

def format_angle_as_turn_sharpiness(angle):
    """Describes an angle as an indication of the sharpiness of a turn. Angle is expected to lie in the range 0 <= angle <= 180."""
    if 0 <= angle < 45:
        return _("slightly")
    elif 45 <= angle < 135: # Normal turn, if someone finds an usable description, feel free to send a PR.
        return ""
    elif 135 <= angle <= 180:
        return _("sharply")
    else:
        raise ValueError(f"Unsupported angle {angle}.")
        
def describe_angle_as_turn_instructions(angle, precision):
    if 180 <= angle <= 360:
        angle = 360 - angle
        direction = _("to the left")
    else:
        direction = _("to the right")
    if config().presentation.use_detailed_turn_directions:
        formatted_angle = format_number(angle, precision)
        return _("{angle} degrees {direction}").format(angle=formatted_angle, direction=direction)
    else:
        angle_description = format_angle_as_turn_sharpiness(angle)
        if angle_description:
            return f"{angle_description} {direction}"
        else:
            return direction

