import webbrowser
from .action import ObjectAction
from ...cp import classproperty

class OpenWikidataRecord(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open wikidata record")

    @classmethod
    def executable(cls, entity):
        return entity.value_of_field("wikidata")

    @classmethod
    def execute(cls, entity, objects_browser):
        return webbrowser.open("https://www.wikidata.org/wiki/{0}".format(entity.value_of_field("wikidata")))