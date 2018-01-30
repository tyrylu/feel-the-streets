from collections import defaultdict
OPERATORS = defaultdict(list)
def _do_operator_registration(operator_class, column_class_names, priority):
    for class_name in column_class_names:
        OPERATORS[class_name].append((operator_class, priority))

def operator_for(*class_names, priority=0):
    def wrap(klass):
        _do_operator_registration(klass, class_names, priority)
        return klass
    return wrap

def operators_for_column_class(column_class_name):
    candidates = OPERATORS[column_class_name] + OPERATORS["*"]
    candidates.sort(key=lambda item: item[1])
    classes = [item[0] for item in candidates]
    return classes