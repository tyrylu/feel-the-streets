import webbrowser
from .action import ObjectAction
from shared.cp import classproperty

class OpenRUIANDetails(ObjectAction):
    @classproperty
    def label(cls):
        return _("Open the ruian register details")

    @classmethod
    def executable(cls, entity):
        return hasattr(entity, "ruian_building_ref") and entity.ruian_building_ref
    
    @classmethod
    def execute(cls, entity):
        return webbrowser.open("http://vdp.cuzk.cz/vdp/ruian/stavebniobjekty/{0}".format(entity.ruian_building_ref))