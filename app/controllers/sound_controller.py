import collections
import random
import attr
import anglr
from ..services import sound
from ..entities import entity_post_move, entity_post_enter, entity_post_leave, entity_rotated
from shared.entities import Road
from shared.entities.enums import RoadType

@attr.s
class SoundController:
    _point_of_view = attr.ib()
    _groups_map = attr.ib(init=False, default=collections.defaultdict(collections.OrderedDict))
    
    def __attrs_post_init__(self):
        entity_post_move.connect(self.post_move)
        entity_post_enter.connect(self.post_enter)
        entity_post_leave.connect(self.post_leave)
        entity_rotated.connect(self._rotated)

    def post_move(self, sender):
        cartesian = sender.position.toCartesian()
        x, y, z = (cartesian.x, cartesian.y, cartesian.z)
        if self._point_of_view is sender:
            sound().fmodex_system.listener().position = [x, y, z]
        if not sender.use_step_sounds:
            return
        group_stack = self._groups_map[sender]
        if len(group_stack):
            group = group_stack[list(group_stack.keys())[-1]]
        else:
            group = None
        if group:
            sound().play_random_from_group(group, x=x, y=y, z=z)

    def post_enter(self, sender, enters):
        if not sender.use_step_sounds:
            return
        base_group = None
        if isinstance(enters, Road):
            if enters.type is RoadType.path:
                base_group = "steps_path"
            else:
                base_group = "steps_road"
        if base_group:
            count = sound().get_group_size(base_group)
            group = "%s.%02d"%(base_group, random.randint(1, count))
            self._groups_map[sender][enters] = group
    
    def post_leave(self, sender, leaves):
        if not sender.use_step_sounds:
            return
        if isinstance(leaves, Road):
            if sender not in self._groups_map:
                print("Already left %s."%sender)
            else:
                del self._groups_map[sender][leaves]

    def _rotated(self, sender):
        if self._point_of_view is sender:
            angle = anglr.Angle(sender.direction, "degrees")
            sound().fmodex_system.listener().forward = [angle.x, 0, angle.y] # The mapping to the mathematical cartesian coordinate system is x,z,y
            sound().fmodex_system.update()