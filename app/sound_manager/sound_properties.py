import attr

@attr.s
class SoundProperties:
    is_3d = attr.ib()
    min_distance = attr.ib()