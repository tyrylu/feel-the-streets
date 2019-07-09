import re
import builtins
import enum

def underscored_to_words(underscored):
    _ = getattr(builtins, "_", lambda s: s)
    underscored = underscored.replace("_", " ")
    underscored = re.sub(r"^\w", lambda m: m.group(0).upper(), underscored)
    return _(underscored)

def format_class_name(name):
    return re.sub(r"([a-z\d])([A-Z])([a-z\d])", lambda m: "%s %s%s"%(m.group(1), m.group(2).lower(), m.group(3)), name)

def get_class_display_name(klass):
    _ = getattr(builtins, "_", lambda s: s)
    return _(format_class_name(klass.__name__))
