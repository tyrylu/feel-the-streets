from PySide2.QtCore import QLocale
import datetime
import os.path
from ..config import Config

LAST_MOTD_FILE = os.path.join(Config.config_path, "last.motd")

def select_message_from_choices(choices):
    locale_name = QLocale.system().name()
    if locale_name in choices:
        return choices[locale_name]
    if "_" in locale_name:
        lang, country = locale_name.split("_")
        if lang in choices:
            return choices[lang]
    return choices["default"]

def get_local_last_motd():
    if not os.path.exists(LAST_MOTD_FILE):
        return 0
    with open(LAST_MOTD_FILE) as fp:
        return int(fp.read())

def save_local_last_motd(timestamp):
    with open(LAST_MOTD_FILE, "w") as fp:
        fp.write(str(timestamp))

class Motd:
    def __init__(self, data):
        localized_message = select_message_from_choices(data)
        self.timestamp = int(localized_message["timestamp"])
        self.message = localized_message["message"]

    @property
    def timestamp_string(self):
        dt = datetime.datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%c")

    @property
    def is_newer_than_last_local(self):
        return self.timestamp > get_local_last_motd()

    def mark_as_seen(self):
        save_local_last_motd(self.timestamp)