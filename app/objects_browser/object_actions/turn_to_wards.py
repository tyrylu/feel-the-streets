from .action import ObjectAction
from ...cp import classproperty
from ...geometry_utils import bearing_to
from ...humanization_utils import describe_entity
from ...services import speech

class TurnToWards(ObjectAction):
    @classproperty
    def label(cls):
        return _("Turn to wards the object")

    @classmethod
    def executable(cls, entity):
        return True

    @classmethod
    def execute(cls, entity, objects_browser):
        closest = objects_browser._person.closest_point_to(entity.geometry)
        bearing = bearing_to(objects_browser._person.position, closest)
        objects_browser._person.set_direction(bearing)
        speech().speak(_("You have been turned to wards {}.").format(describe_entity(entity)))