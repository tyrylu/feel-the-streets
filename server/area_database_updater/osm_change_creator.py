from .osm_change import OSMObjectChange
from .osm_object import OSMObject, OSMRelationMember

class OSMObjectChangeCreator:

    def __init__(self):
        self._action = None
        self._object_kwargs = None
        self._object_kind = None
        self._actions = []
        self.remark_received = False

    def start(self, tag, attrib):
        if tag == "action":
            self._action = OSMObjectChange.parse_obj(attrib)
        elif tag == "new":
            self._object_kind = "new"
        elif tag == "old":
            self._object_kind = "old"
        elif tag in {"node", "way", "relation"}:
            if not self._object_kind:
                self._object_kind = "new"
            self._object_kwargs = attrib
            self._object_kwargs["type"] = tag
            self._object_kwargs["tags"] = {}
            self._object_kwargs["nodes"] = []
            self._object_kwargs["members"] = []
        elif tag == "nd":
            self._object_kwargs["nodes"].append(attrib["ref"])
        elif tag == "member":
            self._object_kwargs["members"].append(OSMRelationMember.parse_obj(attrib))
        elif tag == "tag":
            self._object_kwargs["tags"][attrib["k"]] = attrib["v"]
        elif tag == "remark":
            self.remark_received = True
    
    def end(self, tag):
        if tag == "action":
            action = self._action
            self._action = None
            self._actions.append(action)
        elif tag in {"node", "way", "relation"}:
            obj = OSMObject.parse_obj(self._object_kwargs)
            setattr(self._action, self._object_kind, obj)
            self._object_kind = None
            self._object_kwargs = None

    def new_actions(self):
        while True:
            try:
                yield self._actions.pop()
            except IndexError:
                break