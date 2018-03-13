import enum
import pydantic
from typing import Union, Optional

class ChangeKind(enum.Enum):
    add = 0
    change = 1
    remove = 2

class DictChange(pydantic.BaseModel):
    kind: ChangeKind
    key: str
    old_value: Union[int, float, pydantic.constr(max_length=2**32)] = None
    new_value: Union[int, float, pydantic.constr(max_length=2**32), dict] = None

    @classmethod
    def updating(cls, key, old, new):
        return cls(kind=ChangeKind.change, key=key, old_value=old, new_value=new)
    
    @classmethod
    def creating(cls, key, value):
        return cls(kind=ChangeKind.add, key=key, new_value=value)
    
    @classmethod
    def removing(cls, key):
            return cls(kind=ChangeKind.remove, key=key)
    
    def __str__(self):
        if self.kind is ChangeKind.add:
            return f"Added {self.key} with value {self.new_value}"
        elif self.kind is ChangeKind.remove:
            return f"Removed {self.key}"
        elif self.kind is ChangeKind.change:
            return f"{self.key} changed from {self.old_value} to {self.new_value}"

def diff(old, new, excluded_keys=None, none_in_new_means_removal=True, key_prefix=None):
    if excluded_keys:
        exclude = set(excluded_keys)
    else:
        exclude = set()
    old_keys = set(old.keys()).difference(exclude)
    new_keys = set(new.keys()).difference(exclude)
    added = new_keys.difference(old_keys)
    removed = old_keys.difference(new_keys)
    stayed = old_keys.intersection(new_keys)
    changes = []
    for added_key in added:
        top_level_key = added_key if not key_prefix else "{0}.{1}".format(key_prefix, added_key)
        changes.append(DictChange(kind=ChangeKind.add, key=top_level_key, new_value=new[added_key]))
    for key in removed:
        top_level_key = key if not key_prefix else "{0}.{1}".format(key_prefix, key)
        changes.append(DictChange(kind=ChangeKind.remove, key=top_level_key))
    for key in stayed:
        top_level_key = key if not key_prefix else "{0}.{1}".format(key_prefix, key)
        if old[key] and new[key] is None and none_in_new_means_removal:
            changes.append(DictChange(kind=ChangeKind.remove, key=top_level_key))
        elif isinstance(new[key], dict):
            if old[key] is None or isinstance(old[key], dict):
                old_target = old[key] or {}
            else:
                old_target = {}
            changes.extend(diff(old_target, new[key], key_prefix=key))
        elif old[key] != new[key]:
            changes.append(DictChange(kind=ChangeKind.change, key=top_level_key, old_value = old[key], new_value=new[key]))
    return changes

def _get_change_target(target, key, create_if_missing=False):
    parts = key.split(".")
    intermediary = []
    for part in parts[:-1]:
        if part not in target:
            if create_if_missing:
                target[part] = {}
            else:
                raise ValueError("The path {0} failed to match the target {1}.".format(key, target))
        intermediary.append((part, target))
        target = target[part]
    return intermediary, target

def apply_dict_change(change, target):
    if change.kind in {ChangeKind.add, ChangeKind.change}:
        intermediary, temp_target = _get_change_target(target, change.key, True)
        temp_target[change.key.split(".")[-1]] = change.new_value
    elif change.kind is ChangeKind.remove:
        intermediary, temp_target = _get_change_target(target, change.key)
        del temp_target[change.key.split(".")[-1]]
        for key, container in intermediary:
            if key in container and not container[key]:
                del container[key]
    return target
