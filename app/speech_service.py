import platform
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
        self._speech_history = []

    def speak(self, message, interrupt=False):
        self._speech_history.append(message)
        self._output.speak(message, interrupt=interrupt)

    def silence(self):
        self._output.get_first_available_output().silence()