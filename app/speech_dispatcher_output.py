from accessible_output2.outputs.base import Output, OutputError
try:
    from speechd import Client, SSIPCommunicationError
    has_speechd_api = True
except ImportError:
    has_speechd_api = False

class SpeechDispatcherOutput(Output):
    name = "Linux Speech dispatcher"
    priority = 100
    
    def __init__(self):
        self._client = None
        if has_speechd_api:
            self._client = Client()
        else:
            raise OutputError("Failed to import the speechd module.")
        
    def is_active(self):
        return self._client is not None
    
    def speak(self, message, **kwargs):
        if kwargs.get("interrupt", False):
            self.silence()
        try:
            self._client.say(message)
        except SSIPCommunicationError as e:
            if "retries" in kwargs and kwargs["retries"] < 2:
                self._client = Client()
            else:
                pass

    def silence(self):
        self._client.cancel()

    def close(self):
        self._client.close()

output_class = SpeechDispatcherOutput