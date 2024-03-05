import os
import secrets
from typing import ClassVar
import appdirs
from pydantic import BaseModel
from . import ini_utils

class GeneralConfig(BaseModel):
    client_id: str = ""
    client_secret: str = ""
    language: str = "system"

class NavigationConfig(BaseModel):
    disallow_leaving_roads: bool = True
    try_avoid_sidewalks: bool = True
    step_length: float = 0.7874 # Meters
    stop_interesting_object_search_after: float = 500.0 # meters
    correct_direction_after_leave_disallowed: bool = True
    automatic_direction_corrections: int = 0

class PresentationConfig(BaseModel):
    angle_decimal_places: int = 0
    coordinate_decimal_places: int = 6
    distance_decimal_places: int = 0
    area_decimal_places: int = 0
    near_by_radius: int = 100 # In meters
    interesting_objects_minimum_radius: int = 25 # meters
    play_sounds_for_interesting_objects: bool = True
    announce_interesting_objects: bool = True
    use_detailed_turn_directions: bool = False
    play_crossing_sounds: bool = True
    announce_current_object_after_leaving_other: bool = True
    represent_bearings_as_clock_position: bool = True
    areas_list_max_parents: int = 1
    current_crossing_pitch: float = 1.1
    lands_are_interesting: bool = True
    shops_are_interesting: bool = True
    trashcans_are_interesting: bool = True

class ChangelogsConfig(BaseModel):
    enabled: bool = False

class SoundsConfig(BaseModel):
    enable_hrtf: bool = True

class Config(BaseModel):
    config_path: ClassVar[str] = appdirs.user_config_dir("feel-the-streets", appauthor=False, roaming=True)
    _config_file: ClassVar[str] = os.path.join(config_path, "config.ini")
    general: GeneralConfig = GeneralConfig()
    navigation: NavigationConfig = NavigationConfig()
    presentation: PresentationConfig = PresentationConfig()
    sounds: SoundsConfig = SoundsConfig()
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
    def redis_url(self):
        from_env = os.environ.get("REDIS_URL", None)
        if from_env:
            return from_env
        if not self.general.client_secret:
            raise RuntimeError("Can not create redis connection URL, the client is not created on the server and the REDIS_URL environment variable is not set.")
        return f"rediss://{self.general.client_id}:{self.general.client_secret}@fts.trycht.cz"
        