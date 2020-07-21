import os
import secrets
from typing import ClassVar
import appdirs
import pydantic
from . import ini_utils

class GeneralConfig(pydantic.BaseModel):
    client_id: str = ""

class NavigationConfig(pydantic.BaseModel):
    disallow_leaving_roads: bool = True

class PresentationConfig(pydantic.BaseModel):
    angle_decimal_places: int = 0
    coordinate_decimal_places: int = 7
    distance_decimal_places: int = 1

class Config(pydantic.BaseModel):
    config_path: ClassVar[str] = appdirs.user_config_dir("feel-the-streets", appauthor=False, roaming=True)
    _config_file: ClassVar[str] = os.path.join(config_path, "config.ini")
    general: GeneralConfig = GeneralConfig()
    navigation: NavigationConfig = NavigationConfig()
    presentation: PresentationConfig = PresentationConfig()

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