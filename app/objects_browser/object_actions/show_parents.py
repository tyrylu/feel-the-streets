from .action import ObjectAction
from ...cp import classproperty
from ...services import map
from ...humanization_utils import describe_entity

class ShowParents(ObjectAction):

    @classproperty
    def label(cls):
        return _("Show parents")

    @classmethod
    def executable(cls, entity):
        return map().get_parent_count(entity.id) > 0
    @classmethod
    def execute(cls, entity, objects_browser):
        from .. import ObjectsBrowserWindow
        parents = map().parents_of(entity)
        cls.window = ObjectsBrowserWindow(unsorted_objects=parents, title=_("Parents of {}").format(describe_entity(entity)), person=objects_browser._person)