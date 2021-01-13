import platform
import os
import shutil
import accessible_output2.outputs
from accessible_output2.outputs import auto
from . import speech_dispatcher_output

class SpeechService:
    def __init__(self):
        if platform.system() == "Linux":
            # This hack inserts the speech dispatcher output to the known outputs for accessible_output2 and gets rid of the espeak one, because it does not athere to the output construction protocol, e. g. it does not throw OutputError as it should.
            accessible_output2.outputs.__dict__["speech_dispatcher_output"] = speech_dispatcher_output
            del accessible_output2.outputs.__dict__["e_speak"]
        # Now, we can rely on the standard automatic output selection.
        self._output = auto.Auto()
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
        self._output.get_first_available_output().silence()

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