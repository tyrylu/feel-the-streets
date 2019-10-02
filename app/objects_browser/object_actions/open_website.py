import webbrowser
from .action import ObjectAction
from ...cp import classproperty

class OpenWebsite(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open website")

    @classmethod
    def executable(cls, entity):
        return entity.value_of_field("website") is not None

    @classmethod
    def execute(cls, entity):
        return webbrowser.open(entity.value_of_field("website"))