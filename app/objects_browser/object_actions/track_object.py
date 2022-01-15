from .action import ObjectAction
from ...cp import classproperty
from .. import tracked_object_changed
from ...services import speech

class TrackObject(ObjectAction):
    @classproperty
    def label(cls):
        return _("Track object")

    @classmethod
    def executable(cls, entity):
        return True

    @classmethod
    def execute(cls, entity, objects_browser):
        tracked_object_changed.send(None, entity=entity)
        speech().speak(_("The object has been marked as tracked."))