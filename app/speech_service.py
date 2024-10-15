import platform
import os
import shutil
import locale
from accessible_output2.outputs import auto, speech_dispatcher
from . import qt_output


class SpeechService:
    def __init__(self):
        from .services import config
        if config().presentation.use_accessible_events_for_speech and qt_output.available:
            self._output = qt_output.Output()
        else:
            self._output = auto.Auto()
            o = self._output.get_first_available_output()
            if isinstance(o, speech_dispatcher.SpeechDispatcher):
                lang, _encoding = locale.getdefaultlocale()
                if not lang:
                    lang = "en_US"
                if "_" in lang:
                    lang = lang.split("_")[0]
                o._client.set_language(lang)    
            if platform.system() == "Windows":
                # This hack ensures that win32com does not end up crashing because of some weird corruptions of the gen_py folder.
                gen_py_path = os.path.join(os.environ["TEMP"], "gen_py")
                shutil.rmtree(gen_py_path, ignore_errors=True)
        self._speech_history = []
        self._speech_history_position = 0

    def speak(self, message, interrupt=False, add_to_history=True):
        if add_to_history:
            self._speech_history.append(message)
        self._output.speak(message, interrupt=interrupt)

    def silence(self):
        out = self._output.get_first_available_output()
        if out:
            out.silence()

    def move_to_next_history_item(self):
        if self._speech_history_position == len(self._speech_history) - 1:
            return False
        else:
            self._speech_history_position += 1
            return True         

    def move_to_previous_history_item(self):
        if self._speech_history_position == 0:
            return False
        else:
            self._speech_history_position -= 1
            return True

    def move_to_first_history_item(self):
        if self._speech_history_position == 0:
            return False
        self._speech_history_position = 0
        return True

    def move_to_last_history_item(self):
        last_pos = len(self._speech_history) - 1
        if self._speech_history_position == last_pos:
            return False
        self._speech_history_position = last_pos
        return True

    @property
    def current_history_item(self):
        return self._speech_history[self._speech_history_position]

    def speak_current_history_item(self):
        self.speak(self.current_history_item, interrupt=True, add_to_history=False)