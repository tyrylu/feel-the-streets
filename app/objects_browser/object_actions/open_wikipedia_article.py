import webbrowser
from .action import ObjectAction
from ...cp import classproperty

class OpenWikipediaArticle(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open wikipedia article")

    @classmethod
    def executable(cls, entity):
        return entity.value_of_field("wikipedia") is not None

    @classmethod
    def execute(cls, entity):
        return webbrowser.open("https://wikipedia.org/wiki/{0}".format(entity.value_of_field("wikipedia")))