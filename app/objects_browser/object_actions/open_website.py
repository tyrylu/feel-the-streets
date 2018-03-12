import webbrowser
from .action import ObjectAction
from shared.cp import classproperty

class OpenWebsite(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open website")

    @classmethod
    def executable(cls, entity):
        return hasattr(entity, "website") and entity.website

    @classmethod
    def execute(cls, entity):
        return webbrowser.open(entity.website)