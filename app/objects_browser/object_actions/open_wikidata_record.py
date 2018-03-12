import webbrowser
from .action import ObjectAction
from shared.cp import classproperty

class OpenWikidataRecord(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open wikidata record")

    @classmethod
    def executable(cls, entity):
        return hasattr(entity, "wikidata") and entity.wikidata

    @classmethod
    def execute(cls, entity):
        return webbrowser.open("https://www.wikidata.org/wiki/{0}".format(entity.wikidata))