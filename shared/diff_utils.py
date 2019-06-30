import osm_db

def _get_change_target(target, key, create_if_missing=False):
    parts = key.split("/")
    intermediary = []
    for part in parts[:-1]:
        if part not in target or not isinstance(target[part], dict):
            if create_if_missing:
                target[part] = {}
            else:
                raise ValueError("The path {0} failed to match the target {1}.".format(key, target))
        intermediary.append((part, target))
        target = target[part]
    return intermediary, target

def apply_dict_change(change, target):
    if change.kind in {osm_db.CHANGE_CREATE, osm_db.CHANGE_UPDATE}:
        intermediary, temp_target = _get_change_target(target, change.key, True)
        temp_target[change.key.split("/")[-1]] = change.new_value
    elif change.kind is osm_db.CHANGE_REMOVE:
        intermediary, temp_target = _get_change_target(target, change.key)
        if change.key.split("/")[-1] not in temp_target:
            return target
        del temp_target[change.key.split("/")[-1]]
        for key, container in intermediary:
            if key in container and not container[key]:
                del container[key]
    return target
