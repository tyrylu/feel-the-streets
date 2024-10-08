import logging
import locale
from accessible_output2.outputs.base import Output, OutputError
try:
    from speechd import Client, SSIPCommunicationError
    has_speechd_api = True
except ImportError:
    has_speechd_api = False

log = logging.getLogger(__name__)

class SpeechDispatcherOutput(Output):
    name = "Linux Speech dispatcher"
    priority = 100
    
    def __init__(self):
        super().__init__()
        self._client = None
        if has_speechd_api:
            self._client = Client()
            lang, _encoding = locale.getdefaultlocale()
            if not lang:
                log.info("No default locale found, using en_US as default language.")   
                lang = "en_US"
            if "_" in lang:
                lang = lang.split("_")[0]
            log.info("Setting output language to %s", lang)
            self._client.set_language(lang)
        else:
            raise OutputError("Failed to import the speechd module.")
        
    def is_active(self):
        return self._client is not None
    
    def _sanitize_message(self, msg):
        """Under Linux, Espeak ignores any punctuation mode settings and if a dot is preceded by a right paren, says the dot regardless of any settings."""
        if msg.endswith(")."):
            msg = msg[:-1]
        return msg

    def speak(self, text, **kwargs):
        text = self._sanitize_message(text)
        if kwargs.get("interrupt", False):
            self.silence()
        try:
            self._client.say(text)
        except SSIPCommunicationError as _e:
            if "retries" in kwargs and kwargs["retries"] < 2:
                self._client = Client()
            else:
                pass

    def silence(self):
        self._client.cancel()

    def close(self):
        self._client.close()

    def __del__(self):
        self.close()
output_class = SpeechDispatcherOutput