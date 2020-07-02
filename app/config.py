import os
import configparser
import secrets
import appdirs

class Config:

    def __init__(self):
        self.config_path = appdirs.user_config_dir("fts", appauthor=False, roaming=True)
        os.makedirs(self.config_path, exist_ok=True)
        self._config_file = os.path.join(self.config_path, "config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)
        self._maybe_initialize_values()
    
    def _maybe_initialize_value(self, section, key, default):
        dirty = False
        if not section in self._config:
            self._config[section] = {}
            dirty = True
        if key not in self._config[section]:
            self._config[section][key] = str(default)
            dirty = True
        return dirty

    def _maybe_initialize_values(self):
        need_saving = False
        need_saving = self._maybe_initialize_value("general", "client_id", secrets.token_urlsafe())
        need_saving = need_saving or self._maybe_initialize_value("presentation", "distance_decimal_places", 1)
        need_saving = need_saving or self._maybe_initialize_value("presentation", "coordinate_decimal_places", 6)
        need_saving = need_saving or self._maybe_initialize_value("presentation", "angle_decimal_places", 0)
        if need_saving:
            self._save()

    def _save(self):
        with open(self._config_file, "w", encoding="UTF-8") as fp:
            self._config.write(fp)

    @property
    def client_id(self):
        return self._config["general"]["client_id"]

    @property
    def distance_decimal_places(self):
        return int(self._config["presentation"]["distance_decimal_places"])

    @property
    def coordinate_decimal_places(self):
        return int(self._config["presentation"]["coordinate_decimal_places"])

    @property
    def angle_decimal_places(self):
        return int(self._config["presentation"]["angle_decimal_places"])
    
    @property
    def amqp_broker_url(self):
        return os.environ.get("AMQP_BROKER_URL", "amqps://app:FeelTheStreets@fts.trycht.cz?socket_timeout=2.0") # Maybe store the value in the config too?