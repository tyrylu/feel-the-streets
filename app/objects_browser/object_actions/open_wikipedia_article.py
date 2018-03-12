import webbrowser
from .action import ObjectAction
from shared.cp import classproperty

class OpenWikipediaArticle(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open wikipedia article")

    @classmethod
    def executable(cls, entity):
        return hasattr(entity, "wikipedia") and entity.wikipedia

    @classmethod
    def execute(cls, entity):
        return webbrowser.open("https://wikipedia.org/wiki/{0}".format(entity.wikipedia))