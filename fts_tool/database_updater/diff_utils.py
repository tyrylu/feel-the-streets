import enum
import pydantic

class ChangeKind(enum.Enum):
    add = 0
    change = 1
    remove = 2

class DictChange(pydantic.BaseModel):
    kind: ChangeKind
    key: str
    old_value: pydantic.constr(max_length=2**32) = None
    new_value: pydantic.constr(max_length=2**32) = None

    @classmethod
    def updating(cls, key, old, new):
        return cls(kind=ChangeKind.change, key=key, old_value=old, new_value=new)
    
    @classmethod
    def creating(cls, key, value):
        return cls(kind=ChangeKind.add, key=key, new_value=value)

    def __str__(self):
        if self.kind is ChangeKind.add:
            return f"Added {self.key} with value {self.new_value}"
        elif self.kind is ChangeKind.remove:
            return f"Removed {self.key}"
        elif self.kind is ChangeKind.change:
            return f"{self.key} changed from {self.old_value} to {self.new_value}"

def diff(old, new, excluded_keys=None):
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
        changes.append(DictChange(kind=ChangeKind.add, key=added_key, new_value=new[added_key]))
    for key in removed:
        changes.append(DictChange(kind=ChangeKind.remove, key=key))
    for key in stayed:
        if old[key] != new[key]:
            changes.append(DictChange(kind=ChangeKind.change, key=key, old_value = old[key], new_value=new[key]))
    return changes
