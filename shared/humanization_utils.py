import re

def underscored_to_words(underscored):
    underscored = underscored.replace("_", " ")
    underscored = re.sub(r"^\w", lambda m: m.group(0).upper(), underscored)
    return underscored

def get_class_display_name(klass):
    return re.sub(r"([a-z\d])([A-Z])([a-z\d])", lambda m: "%s %s%s"%(m.group(1), m.group(2).lower(), m.group(3)), klass.__name__)
