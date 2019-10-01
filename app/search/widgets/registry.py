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
    if column_class in WIDGETS:
        return WIDGETS[column_class]
    else:
        for candidate, widget in WIDGETS.items():
            if column_class == candidate:
                return widget