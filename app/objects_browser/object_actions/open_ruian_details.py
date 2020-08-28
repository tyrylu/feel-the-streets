import webbrowser
from .action import ObjectAction
from ...cp import classproperty

class OpenRUIANDetails(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open the ruian register details")

    @classmethod
    def executable(cls, entity):
        return entity.value_of_field("ruian_building_ref") is not None
    
    @classmethod
    def execute(cls, entity, objects_browser):
        return webbrowser.open("http://vdp.cuzk.cz/vdp/ruian/stavebniobjekty/{0}".format(entity.value_of_field("ruian_building_ref")))