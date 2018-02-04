from collections import defaultdict
OPERATORS = defaultdict(list)
def _do_operator_registration(operator_class, column_classes, priority):
    for class_ in column_classes:
        OPERATORS[class_].append((operator_class, priority))

def operator_for(*classes, priority=0):
    def wrap(klass):
        _do_operator_registration(klass, classes, priority)
        return klass
    return wrap

def operators_for_column_class(column_class):
    candidates = []
    for registered_class in OPERATORS.keys():
        if registered_class == "*":
            continue
        if issubclass(column_class, registered_class):
            candidates += OPERATORS[registered_class]
    candidates += OPERATORS["*"]
    candidates.sort(key=lambda item: item[1])
    classes = [item[0] for item in candidates]
    return classes