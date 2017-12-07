import attr
from shared.models.enums import OSMObjectType

@attr.s
class OSMRelationMember:
    type = attr.ib()
    ref = attr.ib()
    role = attr.ib()

    @classmethod
    def from_dict(cls, member_data):
        member_data["type"] = OSMObjectType[member_data["type"]]
        return cls(**member_data)

@attr.s
class OSMObject:
    id = attr.ib()
    type = attr.ib()
    timestamp = attr.ib()
    version = attr.ib()
    changeset = attr.ib()
    user = attr.ib()
    uid = attr.ib()
    tags = attr.ib(default=attr.Factory(dict))
    lat = attr.ib(default=None)
    lon = attr.ib(default=None)
    nodes = attr.ib(default=attr.Factory(list))
    members = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_dict(cls, element_data):
        element_data["type"] = OSMObjectType[element_data["type"]]
        if "members" in element_data:
            element_data["members"] = [OSMRelationMember.from_dict(m) for m in element_data["members"]]
        return cls(**element_data)