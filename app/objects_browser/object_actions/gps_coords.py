from .action import ObjectAction
from ...cp import classproperty
from ...humanization_utils import describe_entity
from ...services import speech

class GPSCoords(ObjectAction):
    @classproperty
    def label(cls):
        return _("GPS coordinates of the object")

    @classmethod
    def executable(cls, entity):
        return True

    @classmethod
    def execute(cls, entity, objects_browser):
        closest = objects_browser._person.closest_point_to(entity.geometry)
        speech().speak(_("{entity} is at latitude {lat} and longitude {lon}.").format(entity=describe_entity(entity), lat=closest.lat, lon=closest.lon))