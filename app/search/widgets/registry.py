WIDGETS = {}

def widget_for(*class_names):
    def wrap(klass):
        for class_name in class_names:
            if class_name in WIDGETS:
                raise RuntimeError("Duplicate widget registration for %s."%class_name)
            WIDGETS[class_name] = klass
        return klass
    return wrap

def widget_for_column_class(column_class_name):
    return WIDGETS[column_class_name]