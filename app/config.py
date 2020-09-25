import os
import secrets
from typing import ClassVar
import appdirs
from pydantic import BaseModel
from . import ini_utils

class GeneralConfig(BaseModel):
    client_id: str = ""

class NavigationConfig(BaseModel):
    disallow_leaving_roads: bool = True
    step_length: float = 0.7874 # Meters
    correct_direction_after_leave_disallowed: bool = True
    automatic_direction_corrections: int = 0

class PresentationConfig(BaseModel):
    angle_decimal_places: int = 0
    coordinate_decimal_places: int = 6
    distance_decimal_places: int = 0
    near_by_radius: int = 100 # In meters
    play_sounds_for_interesting_objects: bool = True
    announce_interesting_objects: bool = True
    use_detailed_turn_directions: bool = False
    play_crossing_sounds: bool = True
    announce_current_road_after_leaving_other: bool = True

class ChangelogsConfig(BaseModel):
    enabled: bool = False

class Config(BaseModel):
    config_path: ClassVar[str] = appdirs.user_config_dir("feel-the-streets", appauthor=False, roaming=True)
    _config_file: ClassVar[str] = os.path.join(config_path, "config.ini")
    general: GeneralConfig = GeneralConfig()
    navigation: NavigationConfig = NavigationConfig()
    presentation: PresentationConfig = PresentationConfig()
    changelogs: ChangelogsConfig = ChangelogsConfig()

    @classmethod
    def from_user_config(cls):
        os.makedirs(cls.config_path, exist_ok=True)
        cfg = cls(**ini_utils.ini_file_to_dict(cls._config_file))
        if not cfg.general.client_id:
            cfg.general.client_id = secrets.token_urlsafe()
            cfg.save_to_user_config()
        return cfg

    def save_to_user_config(self):
        ini_utils.dict_to_ini_file(self.dict(), self._config_file)

    @property
    def amqp_broker_url(self):
        return os.environ.get("AMQP_BROKER_URL", "amqps://app:FeelTheStreets@fts.trycht.cz?socket_timeout=2.0") # Maybe store the value in the config too?