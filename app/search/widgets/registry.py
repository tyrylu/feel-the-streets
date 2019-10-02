from osm_db import Enum

WIDGETS = {}

def widget_for(*classes):
    def wrap(klass):
        for class_ in classes:
            if class_ in WIDGETS:
                raise RuntimeError("Duplicate widget registration for %s."%class_)
            WIDGETS[class_] = klass
        return klass
    return wrap

def widget_for_column_class(column_class):
    # Try a standard field
    if column_class in WIDGETS:
        return WIDGETS[column_class]
    # Try the enum wildcard (we don't want to name all the known enums in the widget registration)
    if column_class in Enum.all_known():
        return WIDGETS["Enum"]
    raise RuntimeError(f"No widget to edit a field of type {column_class}")
