import os
import configparser
import secrets
import appdirs

class Config:

    def __init__(self):
        self._config_path = appdirs.user_config_dir("fts", appauthor=False, roaming=True)
        os.makedirs(self._config_path, exist_ok=True)
        self._config_file = os.path.join(self._config_path, "config.ini")
        self._config = configparser.ConfigParser()
        self._config.read(self._config_file)
        self._maybe_initialize_values()
    def _maybe_initialize_values(self):
        need_saving = False
        if "general" not in self._config:
            self._config["general"] = {}
            need_saving = True
        if "client_id" not in self._config["general"]:
            self._config["general"]["client_id"] = secrets.token_urlsafe()
            need_saving = True
        if need_saving:
            self._save()

    def _save(self):
        with open(self._config_file, "w", encoding="UTF-8") as fp:
            self._config.write(fp)

    @property
    def client_id(self):
        return self._config["general"]["client_id"]

    @property
    def amqp_broker_url(self):
        return "amqps://app:FeelTheStreets@trycht.cz?socket_timeout=2.0" # Maybe store the value in the config too?