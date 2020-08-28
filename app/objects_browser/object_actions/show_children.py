from .action import ObjectAction
from ...cp import classproperty
from ...services import map
from ...humanization_utils import describe_entity

class ShowChildren(ObjectAction):

    @classproperty
    def label(cls):
        return _("Show children")

    @classmethod
    def executable(cls, entity):
        return map().get_child_count(entity.id) > 0
    @classmethod
    def execute(cls, entity, objects_browser):
        from .. import ObjectsBrowserWindow
        children = map().children_of(entity)
        window = ObjectsBrowserWindow(objects_browser.parent(), unsorted_objects=children, title=_("Children of {}").format(describe_entity(entity)), person=objects_browser._person)
        window.show()